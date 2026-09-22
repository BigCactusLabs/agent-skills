# Changelog

One line per change, newest first, prefixed by skill. Details live in each skill's own files.

## 2026-09-22
- orchestrator, codex-orchestrator: replace local file paths, project and client names, and session IDs in the evidence notes with generic descriptions.
- orchestrator: rebase ladders on Opus 5.5 and GPT-6 Sol/Luna — Codex luna-6 `max` → sol-6 `high` → astra `low`/`high`/`xhigh`, no GPT-5.6 rung; Claude opus `medium` → `high` with `pr-reviewer-high` as default judge, sonnet `high` for recon (`scout-high`) and docs sync; retire `implementer-opus-low`, `implementer-sonnet-high`, `scout-low`; sync the installed bundle's `references/` and tested `scripts/dispatch.py`; pins codex-cli 0.155.1, claude-code 2.1.280.
- codex-orchestrator: worker rungs to gpt-6-luna `max` and gpt-6-sol `high` (no GPT-5.6 tier), Claude Opus reviews at `high` for broad/sensitive changes, sol-6 probe note; dated decision in routing history.

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
