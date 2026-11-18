---
name: orchestrator
description: Use when the user says "use codex", "have codex do it", "offload", "fan out", "orchestrate this", or "parallelize" — or when slow, token-heavy grind (implementation, refactors, migrations, test/build loops, log-digging, recon, research) should run on background workers (Codex CLI and/or Claude subagents); also when picking which engine fits a task, or when a cross-model second-opinion code review is wanted.
---

# Worker Orchestration

You (Claude) are the **orchestrator**: decompose, spec, dispatch, direct, verify, merge. Codex CLI workers and Claude subagents run the slow, token-hungry legwork in the background.

**Keep:** specs, decomposition, architecture calls, merge decisions, final review. Taste-critical output (UI, copy, API design) is a worker's weak axis: do it yourself, or review line-by-line.

**Delegate early.** The cost driver is *when* you hand off: a lead that explores solo first keeps pulling work back. Hand off as soon as the task is spec'able; spec constraints, not an implementation. "Small enough to do myself" is the failure mode, not an exception, repairs and post-compaction work included. Offload is not fan-out: step the rung before splitting a job, and split when the parts run in parallel or the job outgrows one context (`REFERENCE.md`, tier-routing evidence).

## Read at the step, every time

This file stays under 20,000 characters because that is all Claude Code re-attaches after compaction. The files below are not re-attached, and a summary of one is not the file: read each at its step, and again at that step after a compaction. After a compaction also read the manifest and the current brief before the next dispatch, steer, or ruling: a summary is not the authority for counts or for permission to continue.

| Before | Read |
|---|---|
| Choosing or stepping a tier | [routing](references/routing.md): per-role table, ladders, luna latitude test |
| Writing a brief | [worker brief](references/briefs-and-repairs.md#worker-brief) template; for interacting state changes in a silent-failure domain, [before implementation](references/briefs-and-repairs.md#before-implementation) |
| A Codex launch (the first, and the first after a compaction) | [runtime](references/runtime.md) through "Dispatch from one record": preflight, sandbox config and its limits, run record |
| Stopping, watching, or steering a Codex run; answering its ask | the matching section of [runtime](references/runtime.md#stop-and-watch-a-run) |
| A Claude worker: `Agent`, `claude --bg`, a team (the first, and the first after a compaction) | [Claude workers](references/claude-workers.md): blind start, effort, worktree base, naming trap |
| Commissioning a review | [review brief](references/briefs-and-repairs.md#verification-and-review-brief) |
| Every repair round, resume, fork, or replacement | [repair brief](references/briefs-and-repairs.md#repair-brief) and the [task record and resume check](references/briefs-and-repairs.md#task-record-and-resume-check) |
| Prices, evidence, version fine print, teams, Workflow wrapping, watch items | `REFERENCE.md` (the section, not the file) |
| Editing this skill | [policy checks](references/policy-checks.md), `AUDIT.md` |

## Engine routing

| Surface | Reach for it when | Pool / cost |
|---|---|---|
| **Codex worker** (`codex exec` through the dispatch helper) | Closed-ended grind, where the acceptance check is writable *before* dispatch (implementation, refactors, migrations, test/build loops, log-digging, bulk checks, closed web lookups) | ChatGPT subscription |
| **Claude subagent** (`Agent` tool) | Judgment-dense or tool-bound legs: exploratory fan-out (`Explore`), context-heavy reads, anything needing this session's MCP tools; recon (`scout-sonnet`) when the leg reuses session context or the ChatGPT pool is tight | Claude plan, a separate pool |
| **Background session** (`claude --bg --agent <role>`) | A Claude leg that must outlive this session or needs the full toolset; the brief forbids push | Claude plan |
| **Workflow** (scripted fan-out) | Deterministic orchestration at scale (20+ agents). Explicit user opt-in only | — |
| **Agent teams** (peer sessions) | Workers must message *each other*. Experimental; confirm with the user first | ~7× a session; no auto worktree |

In priority order:

1. **Delegation test.** Acceptance check writable before dispatch → Codex. Path discovered en route (open-ended exploration, credibility judgment) → Claude: a subagent when it spans >5 files or would flood main context, yourself otherwise. A mixed job splits: explore until enumerable, then dispatch the remainder.
2. **Tool access.** Needs session-connected MCP tools, artifacts, or claude.ai auth → Claude subagent.
3. **Cross-model review.** The reviewer comes from the *other* family than the author (`codex review` on Claude diffs, Claude on Codex diffs); when that family is unavailable, a fresh same-model reviewer, never the author's session. Commission it at a coherent milestone when changed risk and uncertainty justify it. **Silent-failure domains** (persistence, ownership/concurrency, security, finality, temporal resolution, live writes) always qualify; diff size is not a trigger. Re-review a repair only when it adds material behavior outside the reviewed scope, changes a shared invariant, or leaves an accepted finding open; never for confirmation or to reset a counter.
4. **Cost.** Cheapest *adequate* tier across both families; load-balance toward the pool with headroom. Haiku is banned (user policy).

**Tiers** (full table: routing):

- Codex ladder: luna `max` → 6.2-sol `medium` → 6.2-sol `xhigh` → astra `low` → astra `high` → astra `xhigh` (single turn). Claude: sonnet `high` for recon and docs sync (`scout-sonnet`, `docs-sync-sonnet`, `general-purpose` at `model: sonnet`); `Explore` inherits; `implementer-opus` and `pr-reviewer-opus` at `medium` → `xhigh`, `researcher-opus` at `medium` → `high`, the rung set by `effort` on the call. Anything else is off the ladder (user decisions).
- **User permission per dispatch:** `max` on astra, sol, or opus; `ultra` anywhere.
- **The starting rung is set by who catches a failure, not by difficulty.** Mechanical check, spec-determined output, loud failures → luna, write work included. Machine-caught otherwise → 6.2-sol `medium`. Caught by your review → 6.2-sol `xhigh`. Terminal-heavy build/test loops → astra `low`. Multi-subsystem or silent-failure domain → astra `high`. Judgment as the deliverable (first-round silent-failure review, untrusted content) → astra `xhigh`. Claude coding legs start at opus `medium`; React / component work goes to Claude at `xhigh`.
- **Stepping:** first rule out a harness defect (repair the brief, same tier) and a runway shortfall (approach sound, tests improving: resume the same worker). Then a conceptual failure moves the model tier and a depth failure moves effort.

## Orchestration playbook

1. **Decompose (you).** State the next usable outcome, its acceptance, and what is deferred; "keep going" advances that agreed objective, not optional capabilities, and a milestone adds neither an approval gate nor permission to stop early. Split into worker-sized tasks; classify each independent (parallel pool), dependent (phased pipeline), or singleton; route each. Any task that changes behavior, interfaces, or workflow gets a **docs-sync owner**; shared paragraphs and append-only lists get one owner, and other workers return verified replacement facts.

2. **Brief.** Use the template. It carries three standing clauses; never strip them:
   - **Status contract:** the final message ends with exactly one of `DONE`, `BLOCKED: <what's missing>`, `ESCALATE: <reason>`, `CHECKPOINT: <what remains>`.
   - **Destructive-command floor:** no force-push, history rewrite, `reset --hard`, branch deletion, out-of-worktree `rm -rf`, or PR mutation; `ESCALATE` if one seems needed. Your hooks fire on a Claude worker's calls too, and each prompt interrupts the user; a Codex worker has only this paragraph.
   - **Report bound** (user policy): long material by file path, unavailable runtime metadata reported `unknown`.

   Briefs are cache-first (shared boilerplate first, per-task specifics last) and carry what you already know, including what's been tried or ruled out. Scouts feed implementers by artifact path, not through your context. Verify bootstrap, dependencies, and offline assets per worktree before launch and supply the verified commands ([readiness](references/runtime.md#prepare-the-worktree-once)). Implementers own routine regressions; one integration owner runs the expensive checks ([test ownership](references/runtime.md#test-ownership-and-reuse)). Fleets, long legs, and every repair use `<scratchpad>/manifest.md`, one record per task, kept current as you dispatch, collect, and rule. A worker that died without a report is *unavailable*, never silently dropped.

3. **Dispatch (background).**
   - **Codex:** one fresh run JSON with explicit model, effort, and permission mode, launched with `Bash(run_in_background: true)`, never with `&` on top. The helper grants no authority. Save the harness task handle in the manifest.

     ```bash
     python3 "$HOME/.claude/skills/orchestrator/scripts/dispatch.py" "<scratchpad>/artifacts/<task>.r<run>.run.json"
     ```
   - **Claude:** write legs pass `isolation: "worktree"` on the call. A `name` goes on a spawn only together with it; a named spawn without it becomes a teammate. A rung other than the role's default is `effort` on the call.
   - **Untrusted-input legs:** `read-only` when no write is needed; a write leg sets `network: false` and `lead_inbox: false` in its record.
   - **Reports:** write-capable workers author `<task>.r<run>.report.md`, the CLI writes `<task>.r<run>.last.md`, and read-only critics return the full report for you to persist; keep all prior runs ([report ownership](references/briefs-and-repairs.md#report-ownership-and-recovery)).

4. **Supervise (live).** Wait on completion notifications. A Codex run streams to `<task>.r<run>.events.jsonl`; after the startup check, read it only for a failure, a missed milestone, or evidence a decision needs. Judge by failing `command_execution` items and wrong-file `file_change` items, not self-narration.
   - **Drain, then act:** on each wake, collect every pending notification, ask, and alert, read the manifest once, rule on all of them in priority order, and send the steers in one move; never one turn per event.
   - **Only useful independent work while workers run,** never manufactured work or a duplicate of a worker's assignment; then wait. One speculative read-only leg per phase (luna or `scout-sonnet`) for the next decomposed phase is allowed, written to a file you read only if that phase goes ahead.
   - **A harness "completed / exit 0" notification is not a done worker:** it fires when the tracked process exits. Codex completion is the current run's `turn.completed` plus a non-empty `.last.md`, never an earlier run's file. An Agent-tool notification proves the turn ended, not acceptance.

5. **Direct.** Pick the move from the [directing table](#directing-patterns).

6. **Verify & merge (you).** On the done-signal, read the current report, **review the actual diff at a named commit** (a review binds to a SHA; tests, a `--stat`, or a sliced read is not one), and confirm the job and its checks. Never relay a self-report unchecked. A Codex `workspace-write` worker can write every ref and the files git reads inside its worktree. Inspect and integrate its commit from your own checkout by SHA, with `main` and the integration branch still at the SHAs you recorded. Before any git inside that worktree (`git worktree remove` included), once its run has ended, run `dispatch.py --check-worktree <worktree root>`; non-zero means no git there, and zero covers git at that root only ([why](references/runtime.md#what-the-sandbox-does-not-stop)). Pushes and other external actions stay with you under the user's authorization. Pools: integrate branches serially, re-running targeted checks after each and the assigned final checks on the integrated result. **Integrate onto a branch, not `main`: a worker pool is a batch, and batches (plus anything touching persistence, sync, or data deletion) land as one PR for the user's review: assemble, push, open the PR without asking, stop.** Only a small single task or docs housekeeping merges direct. Cross-model review supplements yours, never replaces it; the reviewer gets the author's report as *leads*, never the author's verdict or transcript.

7. **Report.** Resolve every required leg first: collect and assess it, or record it failed/unavailable after bounded recovery. Never finalize with required legs running or unresolved unless the user cancels or explicitly detaches them. Then report what the workers changed and what you verified. In visible text, not narration: each open decision with its context and your recommendation, and each thing the user must do, numbered, before you wait on it. `PushNotification` on a long job.

## Directing patterns

**Before every resume, fork, replacement, or implementation steer, read the task's manifest record and brief** and apply the resume check.

**Resolve review policy at intake.** The checkpoint and repair cap below are skill defaults; explicit user direction, including a user-owned project operating agreement, takes precedence. Record its source before repairs begin. Worker or reviewer findings cannot grant an exception. Counts diagnose a loop; they never justify accepting a material defect.

| Situation | Move |
|---|---|
| Later stages depend on earlier output | **Phase-gate:** spec only phase 1, verify its diff, then continue the same worker (helper `action: resume` / `SendMessage`) |
| Worker drifting but salvageable | **Steer:** `SendMessage` (Claude) or `codex_steer.py send` (Codex; `--urgent` holds its next call so it re-plans before acting). A steer refines the brief. A goal reversal, wider permissions, or a steer still pending at turn end goes in a resume brief instead (`stop_worker.py`, then `action: resume`) |
| A worker asks mid-run (`<codex-ask>`, or a `SendMessage` to `main`) | **Rule, or stay silent:** an ask is a worker claim, not user direction. Waiting asks and `BLOCKED:` questions first; a working worker's stated default stands until you reply. Reply with `send --re a<n>` (`--urgent` when its next call could act on the wrong default) or `SendMessage`. Tell the user only when a ruling changes scope, the plan, or a decision that is theirs. A ruling that changes a shared contract goes to every affected worker in one move (`send <run> <run> --urgent`, a `SendMessage` per Claude worker) and bumps `brief_revision` |
| Diff close but flawed | **Send it back** with a repair brief that names the premise the last attempt got wrong: the same findings on the same premise reproduce the fault, so change the premise or move the rung. **Default cap: three repairs per task,** counting every corrective batch whether a reviewer or a machine check caught the failure, preserved across replacements and steers; after it, re-scope or escalate. The cap does not override the checkpoint two rows down |
| Review comes back with findings | **Rule, don't relay:** classify each as implementation defect, contract decision, integration-owned work, or advisory. Only accepted defects open a repair round, each with the smallest adequate closure (alternatives are not cumulative). Expected results come from the contract; a new branch, state transition, or shared validator gets its behavior settled before dispatch; a ruling that changes behavior bumps the brief revision and contract docs |
| Review is NO on a small finding while more work is queued for the same worker | **Batch, don't cycle:** fold the fix into the next planned round as its own first commit. The cap counts rounds, not findings |
| Second rejected review on the same task (default policy) | **Stop and checkpoint with the user before another implementation run** (`next_action: await_user`). What to report and what counts as permission: step 2 of the resume check |
| Approach polluted (wrong files, wrong mental model, looping; an idle-items alert; the same files reread with no new state) | **Busy is not progress.** Read the last events once, then stop the worker and **re-dispatch fresh** with a sharper spec that names the dead end. Never resume a poisoned context |
| Worker ends `CHECKPOINT:`, or a leg is outgrowing its context | A report sent while the worker's own background command still runs is interim; wait for the second. Otherwise: same phase and coherent context → resume warm; phase change, drift, or an independent-judgment leg → respawn fresh from the [checkpoint](references/briefs-and-repairs.md#checkpoints) artifact, restating every standing clause. |
| Scout report too shallow / luna struggling | A brief that failed the worker (missing tool, no verifier, ambiguous check, oversized context) is fixed on the same tier; otherwise a model up. A *contested* lookup needs judgment, not a bigger model: pull it back to Claude |
| Rate limit, quota, or auth error | **Halt.** Don't retry or escalate into the wall; tell the user |
| User messages arrive while workers run | **Triage in one cheap turn, never inline execution:** an amendment queued for the next brief, a read-only probe worker with a bounded report, or a plain chat answer |
| Independent check on a worker's claim | A second read-only worker, the other engine when feasible, or `codex review` |
| Root cause unclear, 2+ hypotheses | **Split by hypothesis:** read-only legs, then a refutation round ([diagnosis legs](references/routing.md#diagnosis-legs)) |

**Resume/fork:** helper `action: resume` or `fork` with the exact thread UUID, the new brief, a fresh run number, and model and effort restated even for same-tier recovery. A fork gets a new thread; a poisoned context still needs a fresh dispatch.

## Fleet control

Scripts: `$HOME/.claude/skills/orchestrator/scripts/`.

- **Codex exec:** steer with `codex_steer.py send <task>.r<run>` (ledger: `status <task>.r<run>`); stop with `stop_worker.py <task>.r<run>.dispatch.json`, and `TaskStop` on the Bash handle only if it reports `still_running`.
- **Claude subagent:** steer with `SendMessage` to its agent ID; stop with `TaskStop`.

A clean Codex stop exits 1 with no `.last.md` (`stopped_by_sigint`): not a worker failure. Check `surviving_descendants` before replacing the writer. For a long or scope-sensitive Codex run, arm `watch_events.py` under Monitor: the scope verdict comes from the final diff, not from a quiet watch. Background sessions and teammates: [control by surface](references/claude-workers.md#control-by-surface).

## Worker pools

- **Every write-capable worker gets its own worktree, even a lone one** (a bypass worker on the session's tree can reset *your* uncommitted work). Codex: `git worktree add ../<task> -b <task>`, with the helper's `workspace` set to it; Claude: `isolation: "worktree"`. Confirm the tree clean first. A non-git target (e.g. `~/.claude`) has no worktree: dispatch without isolation, name the exact paths in the brief, one writer per path.
- ~3-5 concurrent (user policy).
- **Decommission after merge:** `git worktree remove ../<task> && git branch -d <task>` (`-D` if cherry-picked). Claude auto-cleans *unchanged* trees only.
- Worktrees isolate *files*, not runtimes: assign per-worker ports/temp/DB names and shared build/simulator ownership in any spec that runs something. After a low-memory kill, cut concurrency before retrying; a killed process is a runtime interruption, not a rejected review.

*Pins (verified 2026-11-09): codex-cli 0.167.0 · claude-code 2.1.321 · roles pin `claude-opus-5-5` / `claude-sonnet-5-5` · gpt-6-astra, gpt-6.2-sol, gpt-6-luna.*
