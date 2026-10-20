---
name: task-context-enrichment
description: Enrich existing repository tasks or issues with verified implementation context for future implementers. Use when asked to load tasks with codebase context, prepare a backlog for handoff, or refresh stale implementation briefs. Covers source and test discovery, evidence review, dependencies, and task-note updates; does not execute the underlying tasks or triage their statuses.
---

# Task Context Enrichment

Give the next implementer enough verified context to start at the right boundary: what exists, where to work, what must hold, how to validate it, and what is still unknown. Keep task completion separate from context completion.

## Establish the task set

Read the repository instructions and tracker conventions. Prefer the repository's authoritative task records; do not assume Backlog.md, GitHub, or Linear.

- Honor named IDs and filters. For an unqualified repository-wide request, use open tasks and state that scope; completed tasks are evidence inputs, not edit targets. Include drafts or archived work only when requested.
- Record the checkout revision, branch, relevant dirty inputs, and selected task IDs. Snapshot full records: descriptions, acceptance criteria, plans, existing notes, statuses, assignments, priorities, and dependencies.
- Inspect existing context before adding more. A well-prepared task may need a small correction or nothing. Count reviewed, changed, and deferred tasks separately.
- Write to task records when enrichment is requested. For a draft or review-only request, produce the proposed packets as local artifacts.

Context work does not mark a task In Progress, complete acceptance criteria, change priority, add dependencies, or rewrite scope. Record newly discovered relationships and conflicts in the context. A tracker readiness flag does not show that an owner decision, human review, or external prerequisite is satisfied.

## Delegate discovery

For a large queue with independent groups, delegate factual extraction when session rules permit; keep a small or tightly coupled set local. Use `orchestrator` (or `codex-orchestrator`) for routing, worker lifecycle, and review; this skill defines only the content contract. Group tasks by shared implementation boundary, a few per worker, and give each worker the brief in [references/worker-brief.md](references/worker-brief.md). Workers read repository and tracker state and write proposed packets to their own scratch path. The lead is the only tracker writer.

## Build the implementation context

Read the full task, its relevant dependencies and completed predecessors, then trace current source, tests, commands, and evidence artifacts. Current code establishes behavior; dated notes establish what was measured or decided at the time.

Each packet supplies the useful parts of this structure:

| Part | What the implementer needs |
| --- | --- |
| Current state | Existing behavior, shipped mitigation, missing mechanism, or incomplete evidence gate. |
| Start here | Repository-relative paths and symbols, including callers and sibling paths affected by the same defect. |
| Constraints and dependencies | Invariants, compatibility requirements, related tasks, and named decisions still required. |
| Validation to run | Existing relevant tests and commands, plus missing coverage or measurements, labeled as future work. |
| First step | A bounded action the task already supports, or the exact input needed before it can start. |

Aim for a few useful paragraphs, not a second copy of the description. Let complexity set the length; link and word-count quotas produce padding. Put the source map in the task note itself.

Keep these distinctions:

- **Current versus historical:** a restriction, tool version, test count, or command name in an old note is not current because the note says so. Verify the present code and label dated measurements.
- **Available versus planned:** check that named symbols and commands exist. State access level when an internal hook decides whether a caller can use it. Label missing planned files and unavailable commands as such.
- **Absent here versus absent everywhere:** a fixture or consumer missing from this checkout may live in another repository or store the task names. State what was inspected and how to resolve the reference.
- **Mechanism versus verdict:** an instrument, mitigation, or structural test does not prove quality, root cause, or a promotion decision.
- **Extraction versus design:** do not choose a dependency, API, threshold, or product direction to make a packet look complete. Record the open choice and the evidence it needs. Do not invent uncertainty where the task already decides.

Follow the repository's own privacy, evaluation, and embargo rules. Preparing context is not a reason to open held-out data or rerun a one-time collection.

## Review and integrate

Check the packet itself, not only the worker's report. Verify important current claims against source and every reference against the snapshot. A matching text anchor shows the text exists, not that it is current or supports the claim. Check sibling paths and task coverage as well as individual facts. Fix small, understood errors while keeping the raw report; send a bounded gap back for repair; return contested questions to the lead. If source or task inputs changed, recheck the affected claims.

Read [references/tracker-integration.md](references/tracker-integration.md) before writing. Append a dated context section with the baseline revision through the supported writer, preserving existing content and metadata. On a repeat pass, refresh only a clearly owned context section, or append a short correction with provenance; do not append the same packet twice. Commit, push, or notify only within the user's authorization.

## Verify completion

- Read each changed record back and compare it with the snapshot. Only the intended context and known tracker-managed fields may differ.
- Check task coverage, current paths and anchors, and labeled missing references as separate categories.
- Confirm the changed file or record set matches the intended set and that pre-existing edits survive. Use NUL-delimited Git path output when scripting; task filenames can contain spaces or Unicode.
- Run tracker integrity checks. Run code tests only if this work changed executable behavior; do not report future validation commands as tests run now.
- Collect every worker result before calling the batch complete. Report deferred or unavailable tasks rather than counting them as enriched.

Report the records updated, the checks run, remaining gates, and delivery state, with links to the task records or draft artifacts.
