# Headless Claude reviews

Claude is authorized for independent reviews only. Astra retains scope, findings adjudication, integration, and the user conversation. Implementation and repairs remain with Codex. A review report does not authorize posting a GitHub review, comment, approval, or any external message.

## Review routing

| Review | Model selection | Effort |
|---|---|---|
| Ordinary independent code review | `--model opus` | `high` |
| Broad diff, persistence, concurrency, security, or new shared invariants | `--model opus` | `xhigh` |
| Adversarial, creative review of a complex question or design | `--model claude-fable-5-1` | `medium`; Astra's thought partner |
| Exceptionally difficult question needing extra creative exploration | `--model claude-fable-5-1` | `high`; super thought partner, used selectively |
| WebDev or visual-refinement review, or a user-requested maximum-depth review | Explicit Opus or Fable selection | `max`; user-gated |

These are local routing choices, not benchmark claims or a guarantee that higher effort produces more creative ideas. Opus `max` is off the default ladder: on Arena Agent Work Opus `high` beats `max` (net improvement 11.6% vs 10.4%, P50 cost $4.07 vs $5.48) and the two tie on Text Arena; WebDev is the one measured domain where `max` leads (about 1688 vs 1661). Figures verified at the primaries 2026-09-10; details in the source skill's REFERENCE.md. Claude also exposes `low`; it is not used by default. Medium remains the default thought-partner setting. Astra may select high without further approval when the question needs unusually deep reframing, alternatives remain stuck on the same assumptions, or several competing constraints demand extra exploration. High can be the first choice when justified; do not require a medium pass first or escalate automatically after every disagreement. Pin `claude-fable-5-1` for both roles so the moving `fable` alias cannot select another version. Do not use `ultracode`: it introduces Claude-led workflow orchestration. Pin model and effort at launch and resume, record the resolved model when available, and report any fallback or effort limit rather than claiming the requested setting ran.

Use the thought partner when the uncertainty concerns framing, competing designs, difficult tradeoffs, or an assumption that needs a strong counterargument. No new permission question is needed for this review role. Give Fable the question, goals, constraints, evidence, and current proposal when one exists. Ask it to challenge premises, identify neglected alternatives, construct concrete counterexamples, and suggest evidence or experiments that would distinguish the options. Invite creative hypotheses but label them separately from established facts. Its report should identify the strongest objection, useful alternatives and their tradeoffs, and what evidence would change its assessment. A diff and defect severity labels are unnecessary for conceptual work. Astra evaluates the ideas and owns the decision; Fable neither implements nor delegates.

## Preflight and brief

Check `claude --version`, `claude auth status`, and relevant `claude --help` flags once per session. Do not print account identifiers or credential files. Version 2.1.266 and Claude Max OAuth authentication were verified locally on 2026-09-09; 2.1.267 was installed on 2026-09-10 and still exposes every flag below. Use normal `-p` mode with that authentication: `--bare` skips OAuth/keychain auth and is not a drop-in startup optimization here.

Create a fresh, self-contained review brief with task/revision/generation. For code review, include the user contract, exact diff/base, changed and untracked file inventory, relevant AGENTS.md constraints, and paths to evidence. For committed work, use an isolated checkout at the reviewed revision. For dirty work, use a snapshot containing the actual dirty/untracked inputs or explicitly pause all writers of reviewed paths and record their hashes before and after. A HEAD SHA alone does not identify dirty state. State which tests ran and pass author-reported risks/deviations as unverified leads; omit the author's verdict. For thought-partner review, use the question-and-evidence brief above. Do not ask for a rubber stamp.

For code defects, require severity, exact path/line, trigger, impact, and evidence. Label reproduced defects CONFIRMED and reasoning-only concerns PLAUSIBLE. For either review role, require the reviewer to state evidence gaps and end DONE, BLOCKED, or ESCALATE. No source edits, Git mutations, implementation, agent spawning, or external messages. Claude returns findings or analysis; Astra rules on each before sending a fix to its author.

## Dispatch

Prepare the brief, diff, and output directory first. Run from the intended repository using the shell tool's `workdir`. The default reviewer can read/search files but cannot run shell commands, edit files, or access connectors. Astra supplies the diff and runs any required reproduction commands separately.

```bash
claude -p \
  --model opus --effort high \
  --safe-mode --strict-mcp-config \
  --tools 'Read,Grep,Glob' \
  --allowedTools 'Read,Grep,Glob' \
  --permission-mode dontAsk --permission-prompts none \
  --output-format stream-json --verbose \
  < /absolute/task-scratch/review-brief.txt \
  > /absolute/task-scratch/review.jsonl \
  2> /absolute/task-scratch/review.stderr
```

For the thought-partner option, replace only the model/effort selection with `--model claude-fable-5-1 --effort medium` and supply the conceptual review brief. For the super thought partner, use `--model claude-fable-5-1 --effort high`. Preserve the same tool and permission limits for both.

`--safe-mode` disables discovered customizations while preserving authentication; carry applicable instructions explicitly in the brief. Do not launch the existing `pr-reviewer-high` or `pr-reviewer-xhigh` role files unchanged: both currently set `permissionMode: bypassPermissions`. Their review criteria informed this workflow, but they are not dependencies. The explicit tool list supplies the review boundary without granting Bash. Do not add unrestricted Bash or permission bypass to let the reviewer run tests; bring those requests back to Astra.

Use the shell tool's managed process/session handle to run in the background while Astra does independent work. Do not combine `-p` with `--bg`, append `&`, or confuse the shell session ID with Claude's conversation `session_id`. Track both IDs separately. Poll with waits no longer than 60 seconds and preserve stdout/stderr artifacts.

Parse `system/init` for resolved model, tools, permissions, and advertised capabilities; do not assume it is the first line. Record requested effort separately if applied effort is not exposed. Accept completion only after process exit, a terminal successful result, a nonempty review report, and Astra's inspection. Parse result/error fields; partial assistant text alone is not success. If the reviewed snapshot changed, mark the report stale for changed content. A review's DONE means review work completed, not code approval. Stop on auth/quota/rate-limit errors without an automatic model fallback.

For cancellation, retain the partial stream and exact session handle. SIGTERM ends the process with an unfinished turn and no result; SIGINT or a supported SDK interrupt ends the turn instead. Use only a cancellation mechanism exposed by the active supervisor, inspect the terminal state, and never interpret absence of a result as successful review. Do not start another process against the same conversation while the old one remains active.

## Follow-up

For a specific clarification, run another `claude -p` with `--resume` and the exact conversation ID after the previous process stops. Repeat model, effort, tool restrictions, permission settings, and output flags; use a new brief/generation and artifact path under the same task ID. Apply [communication.md](communication.md) to changed instructions and repair accounting. Do not use `--continue` in a fleet because it selects the most recent conversation.

A returned conversation ID does not prove the session was persisted or is resumable. A local 2026-09-09 test returned `No conversation found with session ID` after a successful review; the cause was not established. Preserve that failed attempt. For necessary follow-up, use a fresh restricted conversation seeded with the saved brief, report, and relevant snapshot; record that context was reconstructed. Do not remove safe mode, widen permissions, or retry the missing session repeatedly to restore continuity.

Use a fresh conversation for a new independent review. Re-review only when a repair adds a mechanism or shared invariant; enumerated fixes get Astra's own review and targeted checks. Existing send-back limits still apply. Claude never fixes its own findings in this workflow.

## Sources and verification

- [Model configuration and effort levels](https://code.claude.com/docs/en/model-config): supported effort settings and model-dependent limits.
- [Programmatic usage](https://code.claude.com/docs/en/headless): print mode, output formats, session resume, and bare-mode authentication.
- [CLI reference](https://code.claude.com/docs/en/cli-reference): model/effort flags, tool controls, safe mode, and incompatible background flags.

Official documentation/local help checked 2026-09-09. Live Fable 5.1 and Opus reviews completed successfully with only Read/Grep/Glob, dontAsk, and no subagents or permission denials. Requested efforts were medium and high respectively; no applied-effort field was exposed. Opus resolved to `claude-opus-5`. A resume attempt failed as described above; cancellation was not exercised. See [smoke-checks.md](smoke-checks.md) for scoped regression checks.
