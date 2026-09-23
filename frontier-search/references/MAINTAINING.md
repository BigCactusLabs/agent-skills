# Maintaining frontier-search

Before shipping changes, check relevant behavior against [evals.md](../evals.md). Use [eval-runbook.md](../eval-runbook.md) for a full pass and record findings under `eval-results/`. Distinguish static rule coverage from behavior actually exercised; unrun scenarios are not passes. Add scenarios for observed failures and update the rule where it applies, rather than maintaining a duplicate failure-mode checklist.

Prefer cutting repetition or tightening a rule over adding one. A zero-fire rule is a cut candidate or an evaluation gap, not automatic permission to delete it. Keep essential decisions in `SKILL.md`; put conditional mechanics in focused references. New rules must be identified as invariants or adaptable defaults. Keep the invariant set small; adaptations use the `*Adapted:*` footer.

Keep measured research rationale in [evidence.md](evidence.md), not the normal-run instructions. Read the primary before adding or reusing a figure, including one supplied by a worker or sweep. Preserve dated verification status and distinguish reports from verified measurements; model agreement alone is insufficient. The 2026-09-22 review found misattributed and invented figures, so carried numbers also need source checks.

Re-verify runtime claims against current tool documentation, not memory. [runtime.md](runtime.md) holds operational guidance; the evidence ledger records its sources. Raw-page retrieval may be necessary when extraction truncates a document.

[models.md](models.md) and [sources.md](sources.md) are dated snapshots. Confirm model availability before dispatch and venue activity before relying on an entry. The pinned sweep example lives in [parallel-research.md](parallel-research.md); source recognition rules in `SKILL.md` take priority over venue examples.
