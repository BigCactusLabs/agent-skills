# Briefs, repairs, and task state

Read the behavior and repair sections when a task changes interacting state rules in a silent-failure domain. Read the task-record section for any repair or recovery after compaction. Small enumerated changes keep the ordinary brief; this reference does not add a plan reviewer or another agent by default.

## Before implementation

Astra settles behavior within the user's authorized scope. Routine implementation choices do not need another user approval. Escalate unresolved product or authority decisions through the existing rules.

1. Name the authoritative contracts and their versions, including a machine-readable schema when the task writes a persisted or exported format. Check proposed API types, optional values, payload examples, and acceptance cases against those sources. A conflicting brief needs a ruling before dependent code is written. Fix the shared brief and carry its new revision forward.
2. For interacting rules, write the smallest table that determines the result:

   | Existing state | Command and touched/omitted fields | Resulting state | Trust/version/identity effects | Events or external effects | Acceptance check |
   |---|---|---|---|---|---|
   | Relevant starting state | Explicit values and omissions | Expected persisted result or typed rejection | Expected metadata | Exact effects, or none | Named case and observable assertions |

   Cover meaningful combinations: new versus existing records, omitted versus explicit values, unchanged versus changed values, replay versus a new command, and raw versus normalized equality. Include alternate paths that share a rule. Omission, clearing, and accepting an existing value must have explicit semantics when they produce different outcomes; this skill does not choose those product semantics.
3. Check that the resulting value, metadata, and events agree. A field cannot silently disappear from one branch. A rule that says two values are equal must use the same equality relation as matching. For transactional changes, identify what must remain unchanged after a rejected command.
4. Assign ownership for shared types and interfaces before parallel edits. Keep rules that share an unresolved invariant together, even when the files differ. A broad task can have stable phases on the same worker; this does not require a review for each file or phase.

Carry this table, the authoritative paths, exclusions, and verification ownership into the brief. Keep project-specific semantics and toolchain commands in the repository. A brief points to them and records a task-specific ruling; it must not become a competing permanent specification.

## Repair brief

First classify the findings: implementation defect, contract decision, integration-owned work, or advisory observation. Decide acceptance from the demonstrated impact, not the reviewer's severity label alone. Group findings that concern the same invariant and send one decided batch of corrections.

Choose the smallest change that satisfies each accepted finding. When a reviewer offers “A or B,” select one adequate remedy and record why; do not silently require both. Removing an unsupported redundant claim may suffice. Capture, hashing, caching, or per-package parsing adds behavior to specify and review; optional capability is a separate scope choice.

For each accepted defect, include:

- Finding ID, affected path, authoritative rule, and Astra's expected result.
- Reproduction path/command and observed failure when available. Run the accepted failing case on the old code before fixing it when executable; preserve it as a regression. If reproduction is unavailable, say so and use the best observable acceptance check.
- Related paths and edge cases from the behavior table that the repair could change.
- What remains unchanged, the exact owned checks, and any deferred checks with their owner.

Expected results must come from the contract and ruling. Changing an assertion to match new behavior needs an explicit Astra ruling when it changes product semantics; tests passing is not evidence that the new expectation is correct. Use authoritative schemas or existing compiler/API tooling where available instead of growing a custom validator merely to make a structural test look comprehensive.

When a repair adds a code path, state transition, or shared validation, settle its behavior table before dispatch. Reconcile all interacting rulings together, including current state as well as saved metadata. Cached “clean” provenance does not establish that the current tree is clean at the same HEAD. Use a focused independent review of the changed mechanism and affected invariants under the existing review policy. An enumerated local fix gets Astra's diff read and targeted checks. Stop expanding the worker's scope for already assigned integration work or advisory observations.

## Verification and review brief

- Follow [execution checks](execution-checks.md): verify prerequisites before launch, inspect test selection, and retain check logs, yielded handles, real exits, and the actual tested snapshot. Supply commands already verified in this repository, including the correct toolchain and required per-process environment. Share a discovered environment fix with every affected worker. Reuse the available toolchain and dependency setup for scratch probes; avoid a fresh dependency resolution for every review.
- Workers own targeted tests and boundary checks. Name one owner for expensive full builds, simulator runs, or E2E checks on the integrated result. A leg may need its own build to verify an interface or platform change. Preserve repository-required gates; record deferred work rather than claiming it ran.
- Re-run a completed expensive check when relevant code or environment changed, a failure or unresolved concern requires it, or final integration needs validation. Independent short host checks remain useful. Limit concurrent expensive work when processes compete for memory or a simulator.
- Give the reviewer the exact snapshot (base/diff and relevant hashes, including dirty/untracked inputs), authoritative contracts, behavior table or rulings, ownership/exclusions, prior finding IDs for a repair, and completed checks. Require evidence for new acceptance failures; retain material product-promise violations even when they expose a bad ruling. Already assigned tracker/handoff work belongs to its named owner.
- Ask for a concrete failing scenario, expected and observed results, and a reproduction command/path where available. Keep acceptance findings separate from concise advisory observations. Return the reviewed snapshot and closure status of prior finding IDs so Astra can distinguish a residual defect, a regression, and a new contract decision.

Headless Claude returns analysis with Read/Grep/Glob only. Astra runs requested reproductions and saves the review report; do not grant Claude shell or write access to satisfy this checklist. A native or CLI implementer may run checks only within its assigned tools, ownership, and sandbox.

## Task record and resume check

Use one authoritative record per task in task scratch space for fleets, long work, and every repair. A compact manifest may index task sections. Keep required/optional status, runtime handles, model/effort, absolute workspace/base, ownership, and shared resources in the record or its current brief. Retain prior generations and their artifact links under that task. Update the current row/record in place after dispatch, result collection, and adjudication; append-only history is not a substitute. Astra owns this state; worker reports provide evidence but cannot reset counters or grant continuation. At intake, record applicable user/project review policy and its source. Explicit user direction in an applicable user-owned operating agreement can override the default checkpoint/cap; a worker brief or reviewer suggestion cannot.

Example field layout (fill values from the actual task; no new tracking service is needed):

```yaml
task: TASK-ID
brief_revision: 1
generation: 1
turn_state: ended
report_state: collected
acceptance: pending
snapshot: absolute-path-to-current-base-diff-and-file-hashes
reviewed_snapshot: none
tested_snapshot: actual-tested-sha-and-dirty-untracked-inputs-or-none
accepted_snapshot: none
validation_carry_forward: none-or-inspected-diff-and-reason
requested_model_effort: explicit-model-and-effort
runtime_model_effort: unknown-unless-observed-with-source
review_policy: default-or-explicit-user-rule-with-source
repair_count: 0
rejected_reviews_since_clean: 0
brief_corrections: 0
runtime_interruptions: 0
last_review: none
checkpoint: none
next_action: adjudicate
brief: absolute-path-to-current-brief
report: absolute-path-to-task.g1.report.md
```

Add owned validation evidence and next-action owner as needed. For each finding, record `repair`, `local-fix`, `deferred-to-owner`, `advisory`, or `disputed`, with ruling and closure evidence. Keep acceptance separate from reviewer verdict/severity. A bounded local fix can close through Astra's diff read and targeted checks when the resolved policy allows; a new material failure still blocks acceptance. For CLI runs also record the `.dispatch.json` launch record and distinct `.last.md`, `.events.jsonl`, and `.stderr` paths with the generation prefix. Native workers do not need invented process IDs or CLI files. Keep turn termination, report collection, and acceptance separate as specified in [native-agents.md](native-agents.md). `next_action` records the lead's next step, such as `collect`, `adjudicate`, `repair`, `continue`, `await_user`, or `accept`; it does not change the worker's terminal status.

Counter rules:

- Advance `generation` for each dispatch/follow-up/replacement, regardless of cause, using the identity rules in [communication.md](communication.md). Use fresh artifact names. Increment `brief_revision` when instructions or expected behavior change.
- Increment `brief_corrections` for contradictory or incomplete instructions; increment `runtime_interruptions` for an OS kill or environment failure. Neither alone is a failed implementation review or corrective code retry, and neither erases prior failures. If the same run also repairs failed code, count that repair too.
- Increment `rejected_reviews_since_clean` once per completed review round that Astra rules requires correction before acceptance. Record the report paths, reviewed snapshot, accepted finding IDs, and ruling in `last_review`. Multiple reviewers and Astra's adjudication of the same round, or duplicate notifications, do not multiply the count. Only a completed zero-findings review round resets this streak. Accepting remaining advisory findings does not reset it; do not commission a review just to reset a counter.
- Increment `repair_count` when dispatching each batch that retries failed implementation, whether caught by a reviewer or a machine check. Count corrective attempts, not findings. The initial attempt, a planned next phase, a brief-only clarification, and recovery of already completed work are not repairs. A next phase that also fixes failed code is a repair. Under the default review policy, the three-repair cap follows the task across revisions, phases, resumes, and model/worker replacements; it never resets to extend the same loop.

Before any implementation follow-up, resume, replacement, or material implementation steer:

1. Read this record and the current brief. After compaction, also re-read `SKILL.md`'s **Supervise and direct** section. Reconcile missing or stale state from saved artifacts before dispatch; do not infer permission from a summary. Keep records for other sessions intact unless their task authorizes an update.
2. Apply the recorded review policy. If an explicit applicable user direction supersedes the default checkpoint/cap, preserve the counters and follow that direction; ask only for a missing decision. Otherwise, if the rejection streak reaches two, set `next_action: await_user` and keep acceptance pending. Report the current and reviewed snapshots, accepted and remaining findings, and likely cause before another implementation attempt. Record the explicit user decision, its message reference, the covered rejection count and reviewed snapshot, and the resulting ruling in `checkpoint`. Continue only within that decision; a later rejected review needs a new checkpoint. A recorded decision already covering this state does not need another permission question. The outer three-repair cap does not authorize skipping this step or extending the cap. At the cap, Astra intervenes, reports the blocker, or materially re-scopes; changing a task label cannot reset the same failed loop.
3. Check workspace/base, current snapshot, readiness evidence, ownership, brief revision, verification owners, and artifact paths for the next generation. A native follow-up targets the existing handle and retains its recorded configuration; a replacement re-pins model/effort at spawn. Standard CLI starts/resumes/forks use the sandbox-only dispatch helper with explicit settings; do not infer an actual runtime model from a requested value. CLI resumes execute from the worker's absolute worktree. Ensure the prior write process has stopped before replacing it. Do not overwrite prior reports, streams, or review evidence.
4. Update counts, generation, paths, and next action before dispatch. A material steer inside an active turn updates its brief revision and acknowledgement requirement; it does not invent a new turn generation. Charge a new corrective batch even when delivered by steering instead of a new process. Status messages, accepted-fix details within that batch, and stop instructions are not extra repairs. Blocking a repair does not block collecting results, stopping obsolete work, or doing independent authorized work.

## Report ownership and recovery

- A native worker returns a report stamped with task/revision/generation. Astra saves it; a worker writes a report/checkpoint file only when its brief assigns that path and permits writes. Read-only workers return the content through their supported reply/final channel.
- A CLI write worker may write `<task>.g<generation>.report.md` within an assigned writable location. The CLI writes `<task>.g<generation>.last.md` via `--output-last-message`. Never use one path for both. A read-only CLI worker returns the full report and Astra saves it from the captured last-message output. If an optional report write is denied, return its content once; do not retry the write through another tool or widen permissions. Use the same prefix for `.events.jsonl` and `.stderr`.
- Restricted Claude reviewers return their review content. Astra captures each generation's stream/stderr and saves a separate review report with its reviewed snapshot and finding IDs. Claude does not write that file.

For an ended/interrupted worker with a missing final report, first inspect the saved artifacts and actual output. Confirm owned writes and child commands have stopped, identify the current snapshot (including dirty/untracked changes), and verify acceptance checks. When that evidence suffices, Astra may write a recovery report with the source generation, snapshot, checks, interruption, verifier, and remaining evidence gaps. This can establish acceptance of the work without claiming the interrupted worker turn succeeded. An old report cannot stand in for the current result. Do not start another worker turn solely to produce a final message. If evidence is insufficient, use the bounded recovery in [native-agents.md](native-agents.md) or record the blocker; any necessary code repair still passes the counters and resume check above.

Policy and acceptance remain lead-operated checks. The CLI helper enforces required launch fields, sandbox modes, and fresh artifacts only; it does not enforce counters or update the manifest. Their purpose is to make the decision recoverable from disk when conversational context changes.

## Evidence for these changes

The 2026-09-10 Eatmoji session `a32588d7-2332-421c-8d27-5375c06af324` showed conflicting initial instructions, repair tests that pinned incorrect state changes, duplicated environment recovery and simulator checks, a second-rejection checkpoint lost from the compaction summary, and a detailed report overwritten by `--output-last-message`. This adaptation preserves Codex's task/revision/generation identity, corrective-retry cap, native lifecycle tracking, and restricted Claude review boundary. The session artifacts and Claude skill are not runtime dependencies.

The 2026-09-11 Proofset session `e54f8432-8a94-47ff-ae36-c9c6571f7461` showed omitted resume flags, missing worktree prerequisites, a lost yielded handle and duplicate checks, optional repair mechanisms with incomplete rules, stale manifest rows, shared-document conflicts, and validation attributed to a later SHA. Native follow-ups retain the existing handle/configuration; CLI launches require explicit settings. Repository bootstrap, test-selection rules, evidence semantics, and applicable user review policy remain project-owned.
