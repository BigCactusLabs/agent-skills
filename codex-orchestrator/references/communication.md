# Messages and handoffs

Use the smallest message that lets its recipient make the next correct decision. Native tools, Codex CLI, and Claude CLI retain their distinct delivery mechanics; this contract does not add API fields or promise exactly-once delivery.

## Identity and message shape

A task ID survives worker replacement. A brief revision changes when instructions change. A turn generation advances on a new dispatch/follow-up, including a follow-up with the same revision. Track acknowledgements and results against all three values; an old revision or generation cannot satisfy the current assignment. Input checkpoints retain their original identity and provenance; a successor's acknowledgement/result carries its new assignment's stamp.

Use this ordinary-text envelope for substantive messages, not every progress update:

```text
Task: catalog-audit | Revision: 3 | Generation: 2 | Kind: decision
Supersedes: revision 2, include-archived instruction only
Change: exclude archived products from the comparison.
Evidence: /absolute/task-scratch/requirements.md
Unchanged: read-only; same input snapshot and assigned product families.
Acceptance delta: report active products only.
Reply needed: acknowledge revision 3 and state the next action.
```

Useful kinds are question, evidence, decision, blocker, acknowledgement, and result. These are labels in the message body, not tool parameters. Address the exact canonical handle returned by the runtime. Never target yourself as a substitute for a user update.

## Important steering

For a material scope, ownership, invariant, or priority change, request one acknowledgement before relying on dependent work. The receiver confirms the adopted revision and next action, or reports why it cannot apply it. Acknowledgement confirms understanding; the final artifact still needs verification. Routine progress and acknowledgements do not require replies.

First verify that the recipient has a reply tool. If absent, a write-authorized worker can record task ID, adopted revision, generation, and next action in its assigned checkpoint/status artifact for Astra to read. If that write is denied, report the denial once in the final BLOCKED/ESCALATE result; do not retry through another tool or widen permissions. Astra can reduce scope to the read-only phase-boundary path: collect a final result stamped with task/revision/generation before starting dependent work. If an early acknowledgement is essential, split the assignment into a short acknowledgement/CHECKPOINT phase and a later work phase with a new generation. Do not assume child commentary reaches Astra, and do not grant new filesystem writes just to imitate a mailbox.

Native `send_message` queues input; successful submission does not prove consumption. If the recipient might finish before consuming work that must happen, use `followup_task`, which can start an idle turn. Never use repeated status messages as a liveness probe. If a send outcome is ambiguous, inspect status/output before one bounded follow-up carrying the same task/revision and an instruction not to repeat completed work. Record that follow-up as a new generation. Do not flood the mailbox or pretend the text envelope provides runtime deduplication.

Apply new user steering first. Label older worker evidence with its revision; carry it forward only if it still applies. A peer's finding is evidence, not an authorization or a new assignment.

## Peer boundaries

By default, workers report to Astra. For a useful dependency, Astra may give two native workers with verified messaging tools each other's canonical handles, a precise factual exchange scope, and a no-reply deadline. If either lacks the tools, use parent-relayed evidence or a named artifact instead; do not dispatch a peer-dependent task. They can ask for a schema, test result, or artifact path while continuing independent work. They cannot assign work, change each other's scope, transfer ownership, or resolve disputed interfaces themselves. A request requiring a new peer turn returns to Astra; workers do not wake idle siblings on their own. If no reply arrives by the assigned deadline or the next dependent step, report the unanswered dependency to Astra and mark that step blocked; do not repeat the send, guess the fact, or wait indefinitely. Astra can supply existing evidence, wake the peer for actual work, or re-plan the dependency.

If a discovery changes another task's assumptions or acceptance conditions, notify Astra immediately with the affected task IDs, evidence, and proposed impact. Copy authorized affected peers when useful; Astra publishes any decision with a new revision. Avoid all-to-all broadcasts, duplicate reports, circular waits, and politeness-only messages. If two peers are blocked on each other, report the dependency to Astra instead of negotiating indefinitely.

Claude reviewers use their CLI input/output and parent-managed resume. Do not expose Claude messaging tools or open inbound peer access merely to match native communication features.

## Repairs and replacements

Send-back content is a delta: task/revision/generation, Astra's ruling, defect/evidence path, changed acceptance check, unchanged constraints, and repair count. The initial attempt is not a repair. Every corrective retry counts against the same task's three-repair cap, including a Luna-to-Terra or Terra-to-Astra replacement. A planned next phase or clarification is not a repair unless it repeats failed work. A second rejected review on the same task stops for a user ruling before any third round (SKILL.md, Supervise and direct); only a round that closes with zero findings resets the count. At the cap, Astra takes over, reports a blocker, or materially re-scopes; changing the worker or task label cannot reset the same failed loop.

The successor receives the actual checkpoint/artifact path, current constraints, evidence gaps, and superseded decisions. Verify that checkpoint identity matches the assigned task and that its revision is the expected prior state. If identity or retry accounting conflicts, report it to Astra before proceeding; never silently inherit a different task ID or discard a retry count. Preserve the checkpoint until the successor demonstrates that it has read the relevant state. Share current facts rather than a full reasoning transcript by default; let the recipient inspect source artifacts when the summary is insufficient.

## Evidence and deferred transport work

The [released Codex message handler](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/tools/handlers/multi_agents_v2/message_tool.rs) distinguishes queue-only from trigger-turn delivery and returns submission success without an applied acknowledgement. The envelope above is our coordination policy.

Keep SDK bridges deferred. Read [external-message-watchlist.md](external-message-watchlist.md) when automatic background-result delivery becomes a real need; it records the benefit, availability checks, and proposed scope. Native Codex messages and [Claude cross-session messages](https://code.claude.com/docs/en/cross-session-messaging) are separate surfaces, not interchangeable transports.
