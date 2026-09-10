# Native Codex agents

Use the exposed `collaboration` namespace directly. Do not call collaboration tools through `functions.exec`, and do not substitute Claude's Agent, SendMessage, TaskStop, or TaskOutput tools.

## Dispatch and context

In the verified runtime, `spawn_agent` accepts `task_name`, `message`, `model`, `reasoning_effort`, and `fork_turns`. Names use lowercase letters, digits, and underscores. Store the returned agent ID or canonical task path; it is the management handle.

An omitted `fork_turns` or `"all"` inherits the parent's model and effort and **does not accept overrides**. Because Astra is the lead and workers are cheaper models, use `fork_turns: "none"` with a self-contained brief, or a positive integer string when a small recent history slice is useful. Never send `model` or `reasoning_effort` with `fork_turns: "all"`.

Example tool arguments for a bounded inventory:

```json
{
  "task_name": "inventory",
  "fork_turns": "none",
  "model": "gpt-5.6-luna",
  "reasoning_effort": "max",
  "message": "Read-only task in /absolute/repo: enumerate config files that reference the deprecated setting. Follow applicable AGENTS.md. Do not edit files or change Git state; do not spawn agents. Return exact paths, line numbers, and matched values. Acceptance: all tracked config paths in the named package examined. End DONE or BLOCKED with the missing input."
}
```

Implementation dispatch uses the full brief in SKILL.md: `gpt-5.6-terra` with `xhigh` for machine-checked legs, `gpt-6-astra` with `low` for review-checked legs. Terra `max` is off the ladder. A context fork is not a filesystem snapshot. Native agents share the directory and filesystem; explicitly tell a worker to set its command working directory to the assigned worktree. There is no native `isolation` argument in this schema.

Only dispatch a concrete independent leg while useful local work remains. Launch bounded siblings up to capacity without waiting for each one's result. With four total runtime slots, Astra plus three workers fills the runtime; do not assume this cap on a different harness. An idle agent and a reusable handle do not by themselves prove that a new slot is available; follow the live capacity/status result.

Check capabilities at both ends. A parent can have `collaboration` tools while its child has no `send_message`; two children reported this in the 2026-09-09 smoke run. Ask the worker to report its reply-tool availability before relying on live acknowledgements or peers. Collect that fact during useful independent work or a bounded checkpoint phase, then authorize any peer-dependent phase. Child commentary is not a confirmed parent-delivery channel. If messaging is absent, use final results and explicitly owned checkpoint/status artifacts; do not invent a tool or assume immediate peer coordination.

## Steering and lifecycle

| Tool | Use |
|---|---|
| `send_message({target, message})` | Queue evidence or corrections to a running worker. Does not start an idle agent or prove the message was applied. |
| `followup_task({target, message})` | Give an existing worker a new phase or repair task; starts it if idle. Delivers to it if running. |
| `interrupt_agent({target})` | Stop current work promptly. The agent remains available. This does not roll back edits. |
| `list_agents({})` | Inspect status or find a management handle when needed; avoid repeated polling. |
| `wait_agent({timeout_ms: 60000})` | Wait for mailbox/new-input activity when local work is exhausted. It is not a query for every agent's terminal state. |

`send_message` is not an idle-worker resume. Use `followup_task` after completion. Neither tool changes a worker's model in this schema: a Luna-to-Terra or Terra-to-Astra escalation requires a new spawn, seeded with the result and failure evidence. Preserve the old worker's artifacts and account for live capacity before replacing it.

Native final-status notifications establish that a worker's turn ended. Check the report's status and actual output to decide whether the assignment passed. An interrupted turn, partial output, BLOCKED, or CHECKPOINT is not DONE. Worker messages can arrive during the lead's turn; incorporate them without losing new user steering.

Track each generation as running or ended, its report as missing, collected, or unavailable after bounded recovery, and acceptance as pending, passed, or failed/blocked. An ended generation stays ended. A late message does not reopen it; explicit follow-up does, with a new generation. Match completion reports and result/acknowledgement artifacts to the current task, revision, and generation; input checkpoints retain their expected prior provenance. An agent-level idle/ended status or an older report cannot establish completion of a newly dispatched generation. Retain required results or explicit failure evidence before the lead's final answer.

After two consecutive 60-second timeouts without new state, call `list_agents` once. Also inspect when a task passes its expected milestone/deadline without progress, even if sibling messages prevent global timeouts. Track that expectation per task, not per mailbox. For an ended generation with a matching report/artifact, collect it; do not wait for another completion event. If a required report is missing, allow one explicit follow-up requesting that generation's existing artifact/result without repeating completed work; label the recovery turn separately and state which generation it recovers. If that fails, preserve the inconsistency, mark the report unavailable and acceptance failed/blocked, and stop the loop. If running, distinguish a known slow command from no observable progress using the task's expected duration and artifacts; silence alone is not a reason to kill it. At the task-specific deadline, inspect once and interrupt only if no useful progress or a safety/scope problem warrants it. Do not alternate identical sends, waits, and interrupts indefinitely.

At capacity failure, inspect active and resident handles before retrying. Queue-only mail can retain completed workers: do not send idle status probes, assume `interrupt_agent` frees a slot, or raise limits as the first fix. Resume only actual pending work with `followup_task`; otherwise serialize remaining work and preserve the blocker. Do not invent a close/drain tool absent from the live schema.

Read [communication.md](communication.md) for revision acknowledgements and authorized peer exchanges. A sibling uses the canonical handle Astra supplied; a relative name may resolve in a different subtree. Interrupted work may leave partial files and commands: inspect their state before resuming or replacing the worker, never assume rollback.

## Independent review

Use `fork_turns: "none"` for a fresh reviewer. Supply the user contract, base/diff, scope, and read-only constraints. Allow tests only where their generated outputs and resource use are permitted. Require each finding to include a path, trigger, impact, and evidence; label reasoning-only suspicions. Do not ask the reviewer to confirm another model's verdict.

## Permission and configuration checks

Native workers inherit the parent's sandbox and live approval overrides. A read-only brief constrains behavior; it does not create a read-only sandbox. If fresh approval cannot be shown, the blocked action fails back to the parent. Do not treat delegation as permission escalation.

If a future harness supports named custom agents, inspect the selected role: its model and effort settings can override explicit spawn values. This session's schema exposes no role-selection parameter; do not invent one.

The documented `agents.max_concurrent_threads_per_session` setting counts spawned threads and excludes the primary. This differs from this session's four total slots. Use the active runtime's counting rules.

Sources checked 2026-09-09: [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents?surface=app), [released event-wait implementation](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/tools/handlers/multi_agents_v2/wait.rs), and [pending-mailbox residency report](https://github.com/openai/codex/issues/32353). The report is not proof of failure in every runtime. Active tool schemas and restrictions take precedence over examples. The newer [unloaded-child roster change](https://github.com/openai/codex/pull/43491) is not assumed present merely because a CLI is installed; retain the manifest across compaction/resume.
