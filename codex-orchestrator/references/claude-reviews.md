# Headless Claude reviews

Claude is authorized for independent reviews, plus one implementation lane: **React and component implementation runs on headless Claude Opus `xhigh`** (user decisions 2026-09-11 and 2026-09-25), in its own worktree, with the same brief, verification-ownership, and review rules as a Codex worker, and its diff reviewed by Codex (cross-family). Astra retains scope, findings adjudication, integration, and the user conversation. All other implementation and repairs remain with Codex. A review report does not authorize posting a GitHub review, comment, approval, or any external message.

## Review routing

| Review | Model selection | Effort |
|---|---|---|
| Independent code review, including broad diffs, persistence, concurrency, security, or new shared invariants | `--model opus` | `medium`; `xhigh` as the retry after a `medium` review fell short, or when the lead judges a review needs more depth; no `high` rung (user decision 2026-09-26) |
| React / component implementation (the only Claude implementation lane) | `--model opus` | `xhigh`; one `xhigh` retry on failure, then the Astra lead decides |
| Adversarial, creative review of a complex question or design | `--model claude-fable-5-1` | `medium`; Astra's thought partner |
| Exceptionally difficult question needing extra creative exploration | `--model claude-fable-5-1` | `high`; super thought partner, used selectively |
| WebDev or visual-refinement review, or a user-requested maximum-depth review | Explicit Opus or Fable selection | `max`; user-gated |

These are user-owned routing choices, not benchmark claims or a guarantee that higher effort produces more creative ideas. Opus `max` stays off the default ladder; dated measurements are in [routing history](routing-history.md). Claude also exposes `low`; it is not used by default. Medium remains the default thought-partner setting. Astra may select high without further approval when the question needs unusually deep reframing, alternatives remain stuck on the same assumptions, or several competing constraints demand extra exploration. High can be the first choice when justified; do not require a medium pass first or escalate automatically after every disagreement. Pin `claude-fable-5-1` for both roles so the moving `fable` alias cannot select another version. Do not use `ultracode`: it introduces Claude-led workflow orchestration. Pin model and effort at launch and resume, record the resolved model when available, and report any fallback or effort limit rather than claiming the requested setting ran.

Use the thought partner when the uncertainty concerns framing, competing designs, difficult tradeoffs, or an assumption that needs a strong counterargument. No new permission question is needed for this review role. Give Fable the question, goals, constraints, evidence, and current proposal when one exists. Ask it to challenge premises, identify neglected alternatives, construct concrete counterexamples, and suggest evidence or experiments that would distinguish the options. Invite creative hypotheses but label them separately from established facts. Its report should identify the strongest objection, useful alternatives and their tradeoffs, and what evidence would change its assessment. A diff and defect severity labels are unnecessary for conceptual work. Astra evaluates the ideas and owns the decision; Fable neither implements nor delegates.

## Preflight and brief

Check `claude --version`, `claude auth status`, and relevant `claude --help` flags once per session. Do not print account identifiers or credential files. Version 2.1.266 and Claude Max OAuth authentication were verified locally on 2026-09-09; 2.1.267 was installed on 2026-09-10 and still exposes every flag below. Use normal `-p` mode with that authentication: `--bare` skips OAuth/keychain auth and is not a drop-in startup optimization here.

Create a fresh review brief with task/revision/generation and explicit scope, permissions, and acceptance. Reference the shared contract and revision instead of duplicating settled background. For code review, include the authoritative contracts and versions, behavior table or relevant rulings, exact diff/base, changed and untracked file inventory, relevant AGENTS.md constraints, ownership/exclusions, and paths to evidence. For a repair, include prior finding IDs and accepted rulings so closure and new defects can be distinguished. Use the [review brief](briefs-and-repairs.md#verification-and-review-brief). For committed work, use an isolated checkout at the reviewed revision. For dirty work, use a snapshot containing the actual dirty/untracked inputs or explicitly pause all writers of reviewed paths and record their hashes before and after. A HEAD SHA alone does not identify dirty state. State which tests ran and pass author-reported risks/deviations as unverified leads; omit the author's verdict. For thought-partner review, use the question-and-evidence brief above. Do not ask for a rubber stamp.

For code defects, require finding ID, severity, exact path/line, trigger, expected and observed results, impact, and evidence. Return the reviewed snapshot and closure status of prior finding IDs. Classify defects, contract decisions, integration-owned work, and advisory observations separately; severity alone does not decide acceptance. Keep material product-promise violations even when a prior ruling was wrong. Already assigned tracker/handoff work stays with its named owner. Where clear, state the smallest adequate closure; label alternative remedies as alternatives and optional capability as advisory. Do not combine every proposed remedy into a required repair or turn each new nit into an acceptance gate. Label reproduced defects CONFIRMED only when supplied reproduction evidence supports them; label reasoning-only concerns PLAUSIBLE. Return any needed reproduction command to Astra instead of executing it. For either review role, require the reviewer to state evidence gaps and end DONE, BLOCKED, or ESCALATE. No source edits, Git mutations, implementation, agent spawning, or external messages. Claude returns findings or analysis; Astra rules on each before sending a fix to its author.

## Dispatch

Prepare the brief, diff, and output directory first. Use fresh task/generation paths for the brief, stream, stderr, and saved review; never overwrite an earlier review. Claude returns review content, and Astra saves the report from the captured successful result. Do not ask the restricted reviewer to write a report file. Run from the intended repository using the shell tool's `workdir`. The default reviewer can read/search files but cannot run shell commands, edit files, or access connectors. Astra supplies the diff and runs any required reproduction commands separately.

```bash
claude -p \
  --model opus --effort medium \
  --safe-mode --strict-mcp-config \
  --tools 'Read,Grep,Glob' \
  --allowedTools 'Read,Grep,Glob' \
  --permission-mode dontAsk --permission-prompts none \
  --output-format stream-json --verbose \
  < /absolute/task-scratch/task.g1.review-brief.txt \
  > /absolute/task-scratch/task.g1.review.events.jsonl \
  2> /absolute/task-scratch/task.g1.review.stderr
```

For the thought-partner option, replace only the model/effort selection with `--model claude-fable-5-1 --effort medium` and supply the conceptual review brief. For the super thought partner, use `--model claude-fable-5-1 --effort high`. Preserve the same tool and permission limits for both.

`--safe-mode` disables discovered customizations while preserving authentication; carry applicable instructions explicitly in the brief. Do not launch the existing `pr-reviewer-med` or `pr-reviewer-xhigh` role files unchanged: both currently set `permissionMode: bypassPermissions`. Their review criteria informed this workflow, but they are not dependencies. The explicit tool list supplies the review boundary without granting Bash. Do not add unrestricted Bash or permission bypass to let the reviewer run tests; bring those requests back to Astra.

Use the shell tool's managed process/session handle as the primary completion signal. Astra may do useful independent work, then wait. Do not combine `-p` with `--bg`, append `&`, or confuse the shell session ID with Claude's conversation `session_id`. Track both IDs separately. Preserve the complete yielded tool result, including its managed process handle, instead of printing only `.output`. Poll that handle within active session wait limits (at most 60 seconds by default), preserving stdout/stderr artifacts. Read startup metadata once, then diagnostic logs only for a failure, a missed expected milestone, or a specific decision that needs evidence. Do not read the event stream between routine waits just to confirm activity; a user update needs no diagnostic call. After an inspection establishes normal progress, return to waiting until completion or a meaningful new condition. When a log tail is needed, use the saved log rather than launching another process.

Parse `system/init` for resolved model, tools, permissions, and advertised capabilities; do not assume it is the first line. Record requested model/effort separately from observed runtime values; keep applied effort unknown if it is not exposed. Update the current task record after dispatch, result collection, and adjudication; a requested setting or appended note cannot replace that state. Accept completion only after process exit, a terminal successful result, a nonempty review report, and Astra's inspection. Parse result/error fields; partial assistant text alone is not success. If the reviewed snapshot changed, mark the report stale for changed content. Save the completed review content as a distinct artifact such as `task.g1.review.md`, stamped with task/revision/generation and reviewed snapshot. A review's DONE means review work completed, not code approval. Stop on auth/quota/rate-limit errors without an automatic model fallback.

For cancellation, retain the partial stream and exact session handle. SIGTERM ends the process with an unfinished turn and no result; SIGINT or a supported SDK interrupt ends the turn instead. Use only a cancellation mechanism exposed by the active supervisor, inspect the terminal state, and never interpret absence of a result as successful review. Do not start another process against the same conversation while the old one remains active.

## Follow-up

For a specific clarification, run another `claude -p` with `--resume` and the exact conversation ID after the previous process stops. Repeat model, effort, tool restrictions, permission settings, and output flags; use a new brief/generation and artifact path under the same task ID. Apply [communication.md](communication.md) to changed instructions and repair accounting. Do not use `--continue` in a fleet because it selects the most recent conversation.

A returned conversation ID does not prove the session was persisted or is resumable. A local 2026-09-09 test returned `No conversation found with session ID` after a successful review; the cause was not established. Preserve that failed attempt. For necessary follow-up, use a fresh restricted conversation seeded with the saved brief, report, and relevant snapshot; record that context was reconstructed. Do not remove safe mode, widen permissions, or retry the missing session repeatedly to restore continuity.

Use a fresh conversation for a new independent review. Apply the [risk-based re-review criteria](briefs-and-repairs.md#verification-and-review-brief), focusing on the changed risk and affected invariants. Bounded fixes get Astra's own review and targeted checks when these establish closure; do not request a confirmatory yes. Astra records one adjudicated rejection per review round and applies the [recorded review policy and resume check](briefs-and-repairs.md#task-record-and-resume-check) before sending any repair. Claude never fixes its own findings in this workflow.

## Sources and verification

- [Model configuration and effort levels](https://code.claude.com/docs/en/model-config): supported effort settings and model-dependent limits.
- [Programmatic usage](https://code.claude.com/docs/en/headless): print mode, output formats, session resume, and bare-mode authentication.
- [CLI reference](https://code.claude.com/docs/en/cli-reference): model/effort flags, tool controls, safe mode, and incompatible background flags.

Official documentation/local help checked 2026-09-09. Live Fable 5.1 and Opus reviews completed successfully with only Read/Grep/Glob, dontAsk, and no subagents or permission denials. Requested efforts were medium and high respectively; no applied-effort field was exposed. Opus resolved to `claude-opus-5`. From Claude Code 2.1.280 (2026-09-22) `--model opus` resolves to `claude-opus-5-5`, which defaults to `medium` effort, so keep `--effort` explicit. A resume attempt failed as described above; cancellation was not exercised. See [smoke-checks.md](smoke-checks.md) for scoped regression checks.
