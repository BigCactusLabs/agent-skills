# Changelog

One line per change, newest first, prefixed by skill. Details live in each skill's own files.

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
