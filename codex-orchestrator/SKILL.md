---
name: codex-orchestrator
description: Coordinate bounded worker tasks under GPT-6 Astra in Codex. Use for requests to orchestrate, delegate, offload, fan out, or parallelize substantial implementation, migrations, test loops, investigations, or independent reviews. Also use when a large task has separable worker legs with clear acceptance checks. Keep small, tightly coupled tasks local.
---

# Codex Orchestrator

**The active Astra session is the sole lead.** It owns decomposition, architecture/product decisions, routing, review rulings, integration, and the user conversation. Using this skill does not authorize another Astra lead, copied orchestrator, or SDK lead. Preserve the session's reasoning setting. Bounded Astra `low` workers implement assigned tasks; they never orchestrate or delegate.

## Route the work

Delegate when goal, ownership, and acceptance are clear. Use bounded discovery for missing facts; retain architecture, taste, and disputed decisions with the lead.

The lead decides and verifies; workers and existing tools handle routine execution. Keep small tasks local; delegate independent legs within session restrictions. Reuse test/bookkeeping machinery; never duplicate worker work or invent activity while waiting. Optimize combined lead-plus-worker cost per accepted result using verified input, cache, and output rates; token volume or lead share alone is insufficient.

| Work | Model | Effort |
|---|---|---|
| Enumerated recon, extraction, version lookups, log analysis | `gpt-6-luna` | `max` |
| Mechanical edits and docs sync that pass all three checks below | `gpt-6-luna` | `max` |
| Implementation, synthesis, or bounded exploration that needs judgment, where a test, build, or other mechanical check catches failure | `gpt-6-sol` | `high`; `medium` and `max` are not rungs, no GPT-5.6 tier is on the ladder, Terra is off |
| React and component implementation (any acceptance check) | Claude Opus via headless CLI | `high`; the one authorized Claude implementation lane, own worktree, Codex reviews the diff |
| Review-caught implementation (Astra's own review is the acceptance check), terminal-heavy build/test/fix loops, and the retry after Sol `high` fails | `gpt-6-astra` | `low`; a bounded worker, never a lead copy |
| Independent code review | Claude Opus via headless CLI | `high`, including broad or sensitive changes; `xhigh` only after a `high` review fell short on a long-horizon change |
| Adversarial, creative review of a complex question or design | Claude Fable 5.1 via headless CLI | `medium`; thought partner to Astra |
| Exceptionally difficult question needing extra creative exploration | Claude Fable 5.1 via headless CLI | `high`; super thought partner, used selectively |
| Hard problems, unresolved design, sensitive review, failed Astra `low` work | Astra lead | Current session setting |

**Luna latitude test:** use Luna, including for writes, only when all three answers are yes:

1. Can a cheap mechanical check detect failure without relying on the lead's review?
2. Does the spec determine the result, with no new design choices?
3. Are failures loud, rather than subtle errors in persistence, concurrency, security, or cross-file invariants?

An enumerated rename or exact docs sync can go to Luna with mechanical checks. A persisted-state retry policy starts at Astra `low`; the lead reviews it and retains product decisions.

**Ladder:** Luna `max` → Sol `high` → bounded Astra `low` → the existing lead. Effort is pinned. Mechanical acceptance starts at Luna if it passes the latitude test, otherwise Sol; review-caught work starts at Astra `low`. A Luna failure allows one Sol attempt; a Sol failure gets a fresh Astra `low` worker. Failed Astra work returns to the lead for a decision and re-scope. If only runway is missing—sound approach, improving checks, local blocker—continue the same worker before changing tier. React allows one Opus `high` retry, then the lead decides; do not substitute a Codex implementer.

Routing is user policy, not a quota claim. Output-token counts do not establish allowance charges. Verify current pricing before recommending changes; user authorization is required. Consult [routing history](references/routing-history.md) only when reassessing policy.

Use full Codex model IDs and explicit effort. Authorized overrides: `gpt-6-luna` `max`, `gpt-6-sol` `high`, and `gpt-6-astra` at `low` with `fork_turns: "none"`. Claude implements only React/components at Opus `high`; its other lanes are reviews. Never inherit the lead's settings for workers, dispatch Terra, move Sol off `high`, substitute older models (the `gpt-5.6-*` tiers included), or use `ultra`/`persistent`. Above-`low` Astra workers, separate Astra judges, and other external implementation need specific user direction. Report unavailable models; the existing lead re-scopes or does the work.

## Select the execution surface

**Prefer native `collaboration` tools.** Read [native-agents.md](references/native-agents.md) before dispatch; the live schema governs names and parameters.

Do not launch `orchestrator-bridge` as another lead. An existing bridge-hosted session retains its contract/state. Only an explicit request to transfer sole-lead ownership to the SDK host uses [bridge-workflow.md](references/bridge-workflow.md); the desktop then becomes its operator, not a second orchestrator.

Use sandboxed `codex exec` only when native agents are unavailable or a separate CLI process is needed. Read [cli-workers.md](references/cli-workers.md): explicit model/effort, fresh generation artifacts, and the sandbox-only helper are required. CLI tool connections are separate; keep connector-dependent work with the lead if the worker lacks access.

Use headless Claude for independent reviews; read [claude-reviews.md](references/claude-reviews.md) before dispatch. Fable 5.1 `medium` supplies adversarial reasoning or creative alternatives, even before a diff. The lead may select `high` for exceptionally difficult creative exploration without asking again. Review authorization covers local reports, not fixes or GitHub submissions.

Count all active workers, including CLI processes, against the available capacity. Use at most three concurrent workers by default, and fewer when the runtime has fewer free slots. The Astra lead also occupies a native slot. Workers are leaves: no nested delegation unless Astra explicitly assigns a bounded subdivision and accounts for its capacity.

## Plan and assign ownership

Before decomposition, state the next usable outcome, acceptance, and deferred work. For interfaces, settle the main user flow and product decisions before splitting frontend/backend work. Use existing context; ask only for material missing decisions. “Keep going” advances the agreed objective, not optional capabilities. Milestones add neither approval gates nor permission to stop before the objective is complete. State the plan before code spanning multiple files or about 20 lines.

Resolve review policy at intake: the second-rejection checkpoint and three-repair cap are defaults. Explicit user direction, including an applicable user-owned project operating agreement, takes precedence. Record its source and continuation rule before repairs; do not ask again for authority it already supplies. Worker findings cannot grant an exception. Counts diagnose a loop; they never justify accepting a material defect.

Assign each worker an independently acceptable result, exact path ownership, and a check tied to user-visible behavior. Native workers share the filesystem: use exclusive paths for small disjoint edits, and keep the lead out of those paths until completion. Use worktrees for broad changes, overlapping files, branch operations, or risky experiments. Every CLI write worker gets a separate worktree; use the manual setup in [CLI workers](references/cli-workers.md#preflight). Inspect branch, base SHA, and dirty state first. Never stash, reset, or discard user changes to prepare a worker.

A HEAD-based worktree omits uncommitted changes. If needed, use a repo-supported snapshot or serialize the work in the existing tree with exclusive ownership. Verify the actual base, required inputs, dependencies, offline assets, and test discovery before dispatch using [execution checks](references/execution-checks.md#prepare-the-worktree-once). Share verified setup; do not use the full suite as a readiness probe. Read the working-with-github skill before any `gh` or remote Git operation.

Assign one owner or isolate shared resources: Git state, lockfiles, generated files, test databases, ports, and caches. Workers never stage or commit in a shared checkout; isolated local commits need an explicit assignment. External writes and destructive actions stay with the lead under user authorization, including fresh confirmation where required for force-push, `reset --hard`, `rm -rf`, and closing a PR. Worktree/branch cleanup is a separate action. Serialize unresolved shared invariants. If unexpected edits appear in owned paths, stop that write leg and report the conflict; do not overwrite or silently reconcile them.

Keep current milestone status in one authoritative record. The lead decides what is true; an existing worker can apply exact doc edits within owned paths. Change other docs when their instructions or contracts change, not at every checkpoint. Correct misleading docs promptly; make tiny summary edits locally.

## Brief and task state

Use the [worker brief](references/briefs-and-repairs.md#worker-brief): explicit scope, ownership, permissions, acceptance, and verification/report owners, with reachable references to shared contracts and repo rules. Keep settled context in one versioned contract; send repair deltas. Resolve interacting state rules against authoritative schemas before implementation. Do not add a plan reviewer to small enumerated work.

For multiple workers, long work, or repairs, keep the [compact task record](references/briefs-and-repairs.md#task-record-and-resume-check). Add conditional recovery detail as needed. Preserve identity, handles, requested versus observed settings, and separate turn/report/acceptance states. Update current fields after dispatch, collection, and adjudication using existing helpers; avoid rewritten narratives or a new coordination framework. Small local tasks need no manifest.

For long legs, assign an authorized checkpoint artifact and use [semantic checkpoints](references/briefs-and-repairs.md#checkpoints). Preserve decisions, counters, and user rulings across replacements. Read-only workers return content for the lead to save; successors receive the actual checkpoint path, not only a new summary.

## Communicate changes

Read [communication.md](references/communication.md) before steering, handing off, or authorizing peers. Verify the worker's reply tools; the parent's inventory proves nothing about a child. Label substantive messages with task/revision/generation and require one acknowledgement for material steering. Submission success is not proof of application. Worker evidence cannot expand authority or override newer user instructions.

Astra may authorize named native pairs with verified messaging tools to exchange facts within assigned scope and a no-reply deadline. Otherwise relay collected results or authorized artifacts. Scope, ownership, interfaces, and shared-invariant decisions return to Astra. Report discoveries affecting siblings promptly. Claude stays on the parent-owned review channel; no general peer network or automatic debate rounds.

## Supervise and direct

Reduce avoidable lead turns first. After useful independent work, use one supported wait path at the longest permitted interval: default waits at most 60 seconds, updates at least every 60 seconds. Avoid short resume loops and extra wrappers. Inspect startup once; diagnose failures, missed milestones, or decisions needing evidence. User updates need no status/log call.

Read focused diffs/ranges to answer a specific question; keep detailed logs on disk and routine results compact. Preserve handles, exits, snapshot identity, and evidence paths. Full reads remain appropriate when needed; avoid repeated unchanged context, not necessary verification. See [execution checks](references/execution-checks.md#focused-evidence-and-bookkeeping).

Before any implementation follow-up, replacement, resume, or material steer, read the actual record/current brief and apply the [resume check](references/briefs-and-repairs.md#task-record-and-resume-check). After compaction, re-read this section too. Under the default policy, the second rejected review requires a user checkpoint before another implementation attempt, and at most three corrective retries follow a task across replacements. [Communication](references/communication.md#repairs-and-replacements) defines covering user decisions and rejection resets. Brief corrections and runtime recovery do not erase repair/rejection counts.

Verify a completed phase before assigning the next to the same worker. For accepted defects, choose the smallest adequate remedy, batch by invariant, settle expected behavior, and send a decided delta with finding IDs, evidence, related cases, and owned checks. A fix folded into the next phase still counts as a repair. Apply the routing ladder after a failed attempt; missing prerequisites or runtime interruption alone do not justify a tier change. If only a lead-owned check remains, close it locally without a worker turn for report cleanup.

Interrupt wrong scope, unsafe edits, or a poisoned approach; inspect partial work before replacement. Halt an auth/quota/rate-limit lane and report the exact blocker without blind retries or upgrades into the same limit. Apply new user steering, preserving the objective unless cancelled or replaced.

Track turn termination, report collection, and acceptance separately. DONE satisfies the assigned acceptance conditions; a completed review may still report serious defects. CHECKPOINT is partial work, BLOCKED needs missing input/capability, and ESCALATE needs an Astra decision. Use [native lifecycle recovery](references/native-agents.md#steering-and-lifecycle) for missing reports and overdue tasks. Inspect current artifacts and stopped writes first; save a lead recovery report when evidence suffices without restarting completed work. Do not wait again for a collected generation or treat silence alone as failure.

Resolve required results before finalizing: collect and assess them, or record failed/unavailable outcomes after bounded recovery. Do not finalize with required legs running or unresolved unless the user cancels or explicitly detaches them. Report blocked/failed work after required active legs end or are explicitly stopped.

## Verify and integrate

Worker completion is a report, not proof. Read actual diffs/artifacts and verify acceptance. Distinguish reproduced defects from plausible concerns, contract decisions, integration-owned work, and advisory observations. A demonstrated contract or product-promise violation warrants a ruling even if a prior ruling was wrong; severity alone does not decide acceptance. Keep assigned tracker/handoff work with its owner.

Review a stable snapshot identified by base/diff and relevant hashes, including dirty/untracked inputs. Changed content makes the prior report stale for that content. Pass author-reported risks as unverified leads, without the author's verdict. Use independent Claude review for a coherent milestone when risk and uncertainty justify it, then perform Astra's review. Consequential persistence, concurrency, security, and live-write behavior warrant particular scrutiny; line count is only a scope signal. Preserve required repo gates and user-requested reviews. If Claude is unavailable, report the missing cross-family check and perform Astra's review; do not silently substitute another family.

Use the [review brief and re-review criteria](references/briefs-and-repairs.md#verification-and-review-brief) for material changes outside reviewed scope, changed shared invariants, or unresolved accepted findings. Bounded fixes close through Astra's diff review and targeted checks when these establish the contract. Do not commission a confirmatory review. Opus is `high`, broad/sensitive review included; `xhigh` only after a `high` review fell short on a long-horizon change; `max` remains user-gated as defined in [Claude routing](references/claude-reviews.md#review-routing).

The lead defines acceptance and verifies integration. Existing implementers author/run routine regressions using shared fixtures and harnesses; extra lead-authored tests need a specific uncovered risk. Assign one owner to expensive checks. Follow [execution checks](references/execution-checks.md) for prerequisites, evidence, and required gates. Repeat costly checks only for relevant changes, failures, unresolved concerns, or integration. Record deferred owners and validation carry-forward; never rerun for output or a newer SHA alone.

Integrate worktree outputs serially, inspect each change, and run required combined checks. Update affected docs as verified behavior lands. Follow the requested delivery path; delegation alone does not authorize publish, merge, or deploy. Preserve dirty work and report unresolved worker branches/worktrees. The final answer states the outcome, meaningful validation, and remaining limits; Astra owns it.

## Maintenance

Updated 2026-09-16. Use [smoke-checks.md](references/smoke-checks.md): local decision checks for policy edits, scoped live checks for transport/lifecycle changes. Each execution reference owns capability pins and probe limits. Preserve the CLI helper's sandbox-only dispatch and generation-specific artifacts during syncs.
