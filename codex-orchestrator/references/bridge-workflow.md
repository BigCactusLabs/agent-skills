# Opt-in orchestrator bridge

Use this route only for an explicit user request to transfer sole-lead ownership to
`orchestrator-bridge`. Invoking the skill in an existing Astra session does not authorize
another lead. Ordinary orchestration keeps the native-worker and headless-review workflow.
If this lead is already hosted by the adapter, follow its developer contract and existing
state; do not start another adapter or move the task to a new identity.

The bridge starts a separate persisted SDK session; it cannot attach to the current desktop
conversation. During an authorized transfer, the desktop stops assigning implementation work
and becomes the process operator and final verifier. The SDK session is then the sole
orchestrator. Never run both as leads for the same task.

## Prepare and start

Read `~/.codex/orchestrator-bridge/README.md` for the current commands, validated runtime,
and limits. Use that repo as the Python module working directory and a separate absolute
scratch directory per orchestration task. Retain the scratch path for every resume.

Use a Python environment with the repo's pinned dependencies. Verify its SDK import, the
selected `codex` binary version, and live model catalog before dispatch. SDK/CLI 0.154.0 is
the pair validated by the September 15 crash pilot; do a bounded compatibility check before
depending on a changed pair. If setup is unavailable, use the manual workflow below.

Before starting, inspect the target checkout, current SHA and dirty files; prepare its
normal prerequisites. Write a bounded task brief with owned paths, verification ownership,
and the applicable review/checkpoint policy. Initialize a new task record only when it does
not already exist. The current CLI stores a `--review-policy` label but does not translate
custom policies into different gates. If the authorized policy differs from the recorded
gates, use the manual workflow until the bridge can represent it correctly. The CLI pattern is:

```text
python -m bridge --scratch <absolute-state-dir> init --task <id> --sha <full-sha> --brief <absolute-brief>
python -m bridge --scratch <same-state-dir> start --repo <absolute-checkout> --codex-bin <verified-binary> --model gpt-6-astra --effort high --sandbox workspace-write --opening "Read the brief at <absolute-brief> and begin."
```

Use the verified environment's Python. Select read-only sandboxing for read-only work.
Keep one supervised `start` process and its original handle. A later `start` with the same
scratch resumes its saved thread. Do not add an opening instruction that restarts completed
work, create a second writer to the same scratch, or remove sandbox/approval controls to
work around an environment failure. Use the supported approval path or manual fallback.

## Operate and verify

The hosted lead must get `DISPATCH-OK` before each implementation worker and use its issued
Task/Revision/Run in briefs and reports. Let the adapter own counters. Keep the existing
model ladder, review policy, evidence checks, and user authorization boundaries.

- Send operator input through `bridge say`; producer results go through the atomic inbox
  path. Tool-output labels do not authenticate a producer or grant authority.
- Use `bridge brief` for a corrected brief and `bridge review` with the exact base/target
  commits and a fresh review generation. The CLI stamps the current brief revision.
- Read the review and check evidence. Record actual failures as well as passes with TESTED;
  require the correct review/test snapshot before ACCEPT. A lead's claim is not execution
  evidence. Retain original process handles and avoid duplicate checks.
- Record a checkpoint with `bridge checkpoint` only for an actual user decision covering
  the recorded rejection count and snapshot. Never reuse a pilot's simulated decision.
- Inspect saved state with `python -m bridge --scratch <absolute-state-dir> status --json` from the
  bridge repo. This read-only command reports full task records, pending events/turns and
  resolved attention turns; it does not start the SDK. Its live multi-file view is
  observational, not atomic. Invalid saved inputs fail without partial JSON output.

## Restart and manual fallback

After a crash, confirm the former adapter and its owned runtime have stopped before resuming
the same scratch. Inspect `state.json`, records, ledger, inbox, and saved turns. Pending
accepted events can be replayed; injection before a crash may already have reached the lead.
Compare durable ruling history with the returned result. Re-emitting the same RULING event
is idempotent; do not invent a new event or reset counters to conceal a replay.

If resume reports that the saved lead is archived, restore that exact task through the
supported Codex CLI or app control, then resume with the same scratch and no new opening.
An archived lead is not a reason to replace its identity or reset task counters.

The owned-turn journal now recovers the exact original response, including a crash before
local response storage and midway through applying commands. Task effects and per-command
receipts share an atomic save. Identical command lines repeated within one response are one
request; later turns remain new requests. Recovery saves gate replies but never sends them,
including DISPATCH-OK. Inspect reserved runs and worker state before continuing; do not
launch another worker merely because a recovered reservation exists.

Missing, in-progress, foreign, or unavailable original history blocks new input. Known
failed/interrupted turns retain their original messages with requires_attention and
terminal_without_protocol; partial commands are not applied. Inspect task and worker state
before continuing. Legacy response files without a journal version are evidence only.

The live pilots cover named process-crash windows. A transport crash before durable turn
association can still require at-least-once delivery. Full-history SDK reads can be unavailable,
and host/power-loss durability is not guaranteed. Preserve evidence and use manual fallback
when the original result cannot be established.

If the bridge is unavailable or recovery is uncertain, stop its supervised process and verify
workers have ended or are safely accounted for. Carry forward the actual task identity,
brief revision, run, review/test evidence, rejection/send-back counts, checkpoint and next
action into the manual native-worker/headless-review workflow. The manual lead must honor
any outstanding checkpoint. Keep the bridge state as evidence; do not start replacement work
against unknown active writers or claim acceptance while evidence is missing. Before returning
to the bridge after manual continuation, reconcile that work with its saved state; do not
resume stale counters or snapshot claims.

Invalid identified retries are terminal failures. Missing/unmatched envelopes remain pending;
restoring a report with only a new event ID can still hit content deduplication. Inspect the
repo's documented recovery limits instead of silently clearing the ledger or resending until
something succeeds. Automatic recovery for those states is not part of this opt-in route.
