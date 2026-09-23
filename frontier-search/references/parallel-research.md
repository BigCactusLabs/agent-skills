# Parallel research and cross-model checks

Read when considering a sweep at probe time or disjoint research legs during expansion. Runtime policy and user authorization govern both subagents and external research CLIs. If restricted, work inline without a warning or degraded-status footer. `low` disables both.

## Disjoint research legs

At `med`/`high`, dispatch only when a gap needs >2 fetches and >1 search **and** separates into non-overlapping players, sub-questions, or source classes. Fan-out buys breadth; do not dispatch to add depth on one thread. Multiple legs may run in parallel at `high` when permitted.

Brief each worker with the exact gap, boundaries, source tiers, frontier posture, and expected output. Require structured findings with direct citations, uncertainty, and unresolved gaps. Carry the citations and material detail into synthesis; do not lose them in summarization. Account for any session-wide search cap shared with workers. Keep exploratory decisions—what to chase next and how to weigh evidence—with the primary researcher.

## Independent cross-model sweep

At `high`, or at `med` for a decision the user will act on, launch a background sweep of the full question **at probe time**, when permitted. Use an installed, authenticated research engine from a **different model family**: Claude primary → Codex/GPT; Codex/GPT primary → Claude. A same-family rerun is not triangulation. Skip silently for pure lookups, `low`, or when no independent engine is available.

Pin model and effort explicitly. The following is the existing Claude-primary → Codex sweep example; confirm availability before use. For another family or unavailable pin, consult the dated [models.md](models.md) reference and verify the replacement against the local CLI/catalog.

```sh
codex exec -s read-only -c 'web_search="live"' \
  -m gpt-5.6-terra -c model_reasoning_effort=max --skip-git-repo-check --json \
  --output-last-message <scratchpad>/codex-sweep-$(date +%s).md \
  "<question + frontier signal posture>" </dev/null
```

Use a unique output path. Reject any sweep file whose modification time predates launch. Use the appropriate capable model in the independent family; a cheap lookup model is not a rigorous synthesis check. CLI sweeps may bill without a consent prompt; use only existing authorization and do not install/authenticate another engine merely to force a sweep.

Run the main loop while the sweep works. At synthesis, compare the tracks:

- **Agreement:** increase confidence only for independent evidence; cite once. Model agreement over the same origin is not new corroboration.
- **New lead:** fetch/verify it before using it as support. A sweep URL or figure is not verified merely because another model supplied it. At cap, retain useful leads as unverified; use only the main loop's remaining wrap-up retrieval allowances.
- **Disagreement:** prioritize primary-source verification in the draft fact-check. If unresolved within budget, report the split and both sources, with access/verification limits explicit.

The main researcher's synthesis remains the answer; the sweep is a check, not a second author. Its background work does not consume the primary loop's expand rounds, but any shared tool caps still apply. Different models can share errors or fail differently; neither model's output substitutes for reading the source.

When dispatch is permitted, a cross-model worker may also handle a closed-ended leg such as version checks or a known list of contested claims. Preserve the same scope, citation, budget, and authorization rules.
