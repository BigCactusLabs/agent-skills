# Changelog

One line per change, newest first, prefixed by skill. Details live in each skill's own files.

## 2026-09-30
- orchestrator: size passes, no routing rule changed. SKILL.md 35,984 → 31,228 bytes: text that repeated a reference now links to it, and rarely used mechanics moved to REFERENCE.md (cross-session `accept` setting, fan-out limits, manual resume/fork flags, JSONL event types, lane-lead fan-out wording). REFERENCE.md 71,903 → 41,987 bytes: superseded pricing (GPT-5.6, pre-5.5 Claude), closed watch items, and GPT-5.6-era and Opus 5 evidence deleted; the evidence sections sit under one "Tier routing evidence" heading. The astra `low` watch item no longer carries a re-rung trigger, since it compared against terra, which is off the ladder.
- codex-orchestrator: headless Claude reviews and the React lane pass `--model claude-opus-5-5` instead of the `opus` alias (effort calibration is per model; a model change is a deliberate edit); the reviewer role note no longer claims a `permissionMode`; flags re-verified on Claude Code 2.1.286.
- orchestrator: GPT-6.1 Sol (`gpt-6.1-sol`, 2026-09-29, sol-6's list price with $0.10 cache reads) replaces `gpt-6-sol` on the Codex ladder: luna-6 `max` → 6.1-sol `high` → 6.1-sol `xhigh` → astra `low` → `high` → `xhigh`. A paired eval on the 15 implementer cases (`orchestrator/evals/`, Codex arms section, `report_codex.py`) had 6.1-sol `xhigh` and astra `low` each pass 14/15 at $0.32 vs $1.07 per run, so review-caught legs now start at 6.1-sol `xhigh` with astra `low` as the retry and the terminal-heavy rung. REFERENCE.md carries the 6.1 Sol pricing, credits, catalog facts (bundled default at `low` since CLI 0.159.1, Luna Reserve, no 6.1 Astra/Luna), and the A/B table; pins move to codex-cli 0.159.2 (`exec` flags unchanged since 0.155.1).
- codex-orchestrator: same rung swap in SKILL.md, cli-workers, native-agents and the helper fixture; routing history records the 2026-09-30 decision and evidence.
- orchestrator: machine-caught Codex rung moved to 6.1-sol `medium` after the same suite ran 6.1-sol `medium` and `high` (all four arms 14/15 with the same miss; mean $0.17 / $0.27 / $0.32 / $1.07 for `medium` / `high` / `xhigh` / astra `low`). Ladder is now luna-6 `max` → 6.1-sol `medium` → 6.1-sol `xhigh` → astra `low` → `high` → `xhigh`; `high` is not a rung; the lane-lead A/B pair is astra `high` vs 6.1-sol `xhigh`. Four-arm table in `orchestrator/evals/` and REFERENCE.md.
- codex-orchestrator: same `medium` rung in SKILL.md, cli-workers, native-agents and the helper fixture; routing history records the four-arm result.
- orchestrator: Sonnet 5.5 checked (released 2026-09-28 at Sonnet 5's price; `sonnet` alias resolves to it since Claude Code 2.1.284): no Claude rung change. Scouts and docs sync stay at sonnet `high`; no Sonnet implementer, reviewer or `xhigh` scout rung, since Opus 5.5 `medium` dominates on cost per task. Figures and caveats in REFERENCE.md; pins footer to claude-code 2.1.286.

## 2026-09-27
- orchestrator: publish the Opus 5.5 effort-tier eval summary in `orchestrator/evals/` (README, `report.py`, per-run aggregates; fixture code and reports withheld, private-repo cases renamed). Implementers passed 14/15 at `medium`, `high` and `xhigh`; reviewer found-rate differences across efforts are within noise, `high` matches `medium` on recall at 1.5× the cost, and `medium` → `xhigh` matches flat `xhigh` recall at lower cost. REFERENCE.md's Claude-side rungs note cites it; the 2026-09-25 and 2026-09-26 retirements now have evidence.
- orchestrator: `pr-reviewer-max` description no longer claims max measurably beats lower efforts on WebDev review; that gate rests on the Arena WebDev basis, which the eval did not cover.
- codex-orchestrator: routing history and the Claude review table cite the 2026-09-27 eval behind the `medium` → `xhigh` review ladder.

## 2026-09-26
- orchestrator: Claude reviewers are opus `medium` → `xhigh`. New `pr-reviewer-med` is the default for every review; `pr-reviewer-xhigh` is the retry, or used when the orchestrator judges a review needs more depth; `pr-reviewer-high` is retired. `pr-reviewer-max` stays user-gated.
- orchestrator: sync the 2026-09-25 implementer change — `implementer-opus-high` retired; the Claude implementer ladder is opus `medium` → `xhigh`, and `implementer-opus-xhigh` takes the retry and all React / component work.
- codex-orchestrator: headless Claude reviews run Opus `medium`, with `xhigh` as the retry; no `high` review rung. Also syncs the 2026-09-25 move of the React lane from Opus `high` to `xhigh`.

## 2026-09-24
- orchestrator: reviewer roles may add one detached worktree under the scratch folder to run code at the reviewed commit, and may build throwaway git repos there. REFERENCE.md describes the optional role guard after a strictness pass and an adversarial review: what it unwraps, the throwaway-repo and `cd` rules, and replay results.
- orchestrator: role latitude pass. Role bodies split fixed rules (read-only floor, no git/PR mutation, status line) from defaults the brief overrides (scope, method, source window, return shape, report path). New roles: `implementer-opus-xhigh`, `docs-sync-sonnet-high`, and `researcher-opus-high`, which is now shipped; the med and high researcher descriptions route differently. Researchers preload frontier-search and may write one report file. Reviewers accept plans, specs, and uncommitted changes. `scout-high` gets an exact-name allowlist of Linear, Google Drive, and Claude Docs read tools. Implementers get an isolation-worktree fallback and a non-git mode. `permissionMode` is dropped (ignored since 2.1.267). The read-only roles reference an optional `role-guard.py` PreToolUse hook that fails open when absent. Report-writing roles say Claude Code's "no report files" subagent note doesn't cover their report. REFERENCE.md now says role edits take effect at the next turn boundary. Two policy-check rows added.

## 2026-09-23
- orchestrator: Opus 5.5 prompt audit — the brief rule "on ambiguity, stop and report; never improvise" and the implementer roles' "zero taste decisions" become "inspect unknown values, don't guess", with routine choices left to the worker; dates and the sol probe story moved out of SKILL.md; runtime.md points at the footer's codex-cli pin and the `unittest` command; REFERENCE.md drops the superseded Fable-5.1-lead instructions and the pre-2.1.267 effort conditions.
- frontier-search: sync the installed skill — compact SKILL.md with operational detail in new `runtime.md`, `parallel-research.md`, and `MAINTAINING.md` references; 2026-09-22 eval results (local run paths shown as `<run-dir>`); `opus` alias now Opus 5.5 in models.md; output shapes without word-count ranges (evals not re-run for that change).
- linear-workflows: sync the installed skill — tool tables that name the host (Codex app vs Claude), a raw-GraphQL escape hatch (`scripts/linear-gql`, key read from macOS Keychain), updated Codex default prompt, and the connector-drift rule stated without the May 2026 incident.
- working-with-github: sync the installed skill, adding the `cli-and-api` reference.

## 2026-09-22
- orchestrator, codex-orchestrator: replace local file paths, project and client names, and session IDs in the evidence notes with generic descriptions.
- orchestrator: rebase ladders on Opus 5.5 and GPT-6 Sol/Luna — Codex luna-6 `max` → sol-6 `high` → astra `low`/`high`/`xhigh`, no GPT-5.6 rung; Claude opus `medium` → `high` with `pr-reviewer-high` as default judge, sonnet `high` for recon (`scout-high`) and docs sync; retire `implementer-opus-low`, `implementer-sonnet-high`, `scout-low`; sync the installed bundle's `references/` and tested `scripts/dispatch.py`; pins codex-cli 0.155.1, claude-code 2.1.280.
- codex-orchestrator: worker rungs to gpt-6-luna `max` and gpt-6-sol `high` (no GPT-5.6 tier), Claude Opus reviews at `high` for broad/sensitive changes, sol-6 probe note; dated decision in routing history.

## 2026-09-19
- working-with-github: sync the September 19 audit and compact entrypoint, with focused PR/issue, Actions, stack, and agent references plus source evidence.

## 2026-09-16
- codex-orchestrator: prioritize fewer avoidable lead turns and total cost per accepted result; reuse contracts, test harnesses, and evidence tools, with routine tests/docs owned by existing workers and independent lead acceptance.
- codex-orchestrator: keep the invoking Astra session as sole lead with bounded workers; shorten the entrypoint and sync proportional supervision, risk-based review, compact task records, and dated routing evidence.

## 2026-09-15
- codex-orchestrator: sync the installed bundle with current worker routing, task/review evidence rules, tested sandboxed dispatch helper, and the completed Pilot 4 recovery/status workflow.

## 2026-09-10
- codex-orchestrator: add the Codex-native orchestration skill and its references and discovery metadata.
- orchestrator: ship the nine standing subagent role files in `orchestrator/agents/`; REFERENCE.md templates replaced by a pointer; README install line.
- orchestrator: Claude ladder rebuilt from verified public benchmarks (sonnet low → sonnet high → opus low → medium → high → xhigh; sonnet xhigh/max and opus max off the ladder, opus max user-gated); new implementer-sonnet-high / implementer-opus-low / implementer-opus-high roles; send-back cap (second rejected review stops for a user ruling); Claude tier routing evidence section.

## 2026-09-09
- orchestrator: pins codex-cli 0.153.4 / claude-code 2.1.267; task id, repair count, reviewed-SHA manifest columns; send-back rulings and task-scoped convergence fuse; harness-defect escalation exit; provisional luna long-context gate; `codex mcp-server` deprecation; review/repair and tier-routing evidence sections; −3.3% size pass.

## 2026-09-04
- orchestrator: GPT-6 Astra overhaul — astra @ high replaces sol for hard cases, astra @ xhigh for judge/repair/untrusted-input legs; pins codex-cli 0.153.3 / claude-code 2.1.261; `--title` review fix; −10% size pass.

## 2026-09-02
- working-with-github: allow AI co-authorship trailers.
- frontier-search: draft fact-check, coverage plateau/Overrun, runtime facts, eval pass.
- working-with-github: added.

## 2026-09-01
- orchestrator: codex 0.152.0 / claude-code 2.1.257, pricing refresh; −10% size pass.
