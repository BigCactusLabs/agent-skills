# Bounded orchestration checks

Run relevant cases after changing message, lifecycle, handoff, or transport behavior. Do not run the entire set for copy edits. These are live agent exercises, not tests that match the skill's wording. They consume model usage; use one or two Luna workers for mechanical fixtures, with Astra doing useful local validation alongside them. Use Claude only for review cases. Never reproduce an unbounded mailbox/wait loop.

Create unique scratch fixtures outside production repositories. Record the date, exposed runtime/model metadata, task/revision/generation, handles, actual result, and pass/fail/not-run per case. Keep raw output in scratch space. Report partial coverage honestly; a shell syntax check cannot pass a message-delivery case.

| Case | Exercise | Observable pass condition |
|---|---|---|
| New worker | Give a worker a short local dataset and an independent expected result. | Result matches fixture; turn ends; Astra collects it and records acceptance. |
| Running steering | Check the child's reply tools; during a bounded staged task, change one input-selection rule and request a revision acknowledgement. A short checkpoint pause is acceptable in this fixture. | Worker acknowledges via a supported reply tool or owned artifact and its final result applies the new rule; mark the unavailable channel untested. Submission success alone is insufficient. |
| Read-only acknowledgement fallback | When reply tools are absent and an artifact write is unavailable/denied, reduce scope to a read-only CHECKPOINT phase, then assign dependent work separately. Do not manufacture a permission violation to test this. | Denial is reported, no rejected write is retried, matching task/revision/generation acknowledgement is collected before work begins, and the later generation returns the correct result. |
| Idle follow-up | After collecting that result, assign the same worker a second phase with `followup_task`. | The same handle starts a new generation and returns the new phase result; no queue-only idle probe is needed. |
| Completion collection | Observe the ended generation through status and its report; distinguish an old report from a newly dispatched generation. | Astra records the matching generation's result and does not continue waiting for its completion event; unrelated mailbox activity does not conceal an overdue task. |
| Authorized peer | Verify both workers' messaging tools, then give a named pair a factual scope; one holds needed input. Include a bounded no-reply variant when changing peer rules. | Request/reply stays within scope; decisions or unanswered dependencies return to Astra. If tools are absent, record direct peer exchange unavailable and verify parent/artifact relay separately. No assumed fact, repeated send, or sibling wake-up. |
| Interruption | Have a scratch-only worker save a small partial artifact, then enter a bounded pause; interrupt its turn. | Partial artifact survives; interrupted status is not DONE; no replacement starts against still-running writes. |
| Checkpoint replacement | Give a fresh worker the checkpoint path and newer revision; retain task identity/repair count. | Successor uses the actual saved state and new rule, does not redo completed work, and preserves retry accounting. |
| Stale review | Record a fixture hash, obtain a bounded reviewer report, then deliberately change the fixture. | Astra invalidates the report for the changed snapshot; reviewer DONE is not treated as code approval. |
| Claude transport | Run the restricted read-only command on a harmless fixture. | Successful process/result, nonempty report, expected model/tool inventory, and no prohibited work. |

Do not require a particular sentence or hidden reasoning trace. Verify values, artifacts, revisions, permissions, and lifecycle outcomes. If a real upstream fault appears, stop the affected case after one bounded diagnosis; do not widen permissions or switch to a forbidden surface to finish the test.

For optional Claude resume/cancellation checks, run only when those mechanics changed or a failure warrants it. Preserve the exact conversation ID and old output, ensure the original process stopped, and validate the new generation separately. Test SDK bridges only after explicitly adopting one and verifying its installed capabilities.
