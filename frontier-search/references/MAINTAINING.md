# Maintaining frontier-search

Before shipping, check affected behavior against [evals.md](../evals.md); a full pass follows [eval-runbook.md](../eval-runbook.md), with findings in `eval-results/`. Unrun scenarios are not passes, and results vary between runs of one prompt, so rerun before treating one pass or failure as settled. For an observed failure, add a scenario and fix the rule; keep no separate failure checklist.

Prefer cutting repetition or tightening a rule over adding one; a zero-fire rule is a cut candidate or an eval gap, not automatic deletion. Essential decisions go in `SKILL.md`, conditional mechanics in focused references. Mark each new rule invariant or adaptable default; keep invariants few.

Measured rationale lives in [evidence.md](evidence.md), not the normal-run instructions. Read the primary before adding or reusing a figure, including one from a worker or sweep; the 2026-09-22 review found misattributed and invented carried figures. Preserve dated verification status and separate reports from verified measurements; model agreement alone is insufficient.

Re-verify runtime claims against current tool docs (raw pages when extraction truncates), not memory; [runtime.md](runtime.md) holds the guidance, the ledger its sources.

The model pins in [parallel-research.md](parallel-research.md) and the source guides ([sources.md](sources.md), [sources-frontier.md](sources-frontier.md), [sources-research.md](sources-research.md)) are dated snapshots: confirm model availability before dispatch and venue activity before relying on an entry. `SKILL.md` recognition rules outrank venue examples. Source guides keep only source-specific facts; general evidence caveats belong in `SKILL.md`.
