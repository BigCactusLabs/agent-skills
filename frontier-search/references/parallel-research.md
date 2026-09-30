# Parallel research and cross-model checks

Read when considering a sweep at probe time or disjoint research legs during expansion. Runtime policy and user authorization govern both subagents and external research CLIs; when either is restricted, work inline without a warning or degraded-status footer. `low` disables both.

## Disjoint research legs

At `med`/`high`, dispatch only when a gap needs >2 fetches and >1 search **and** separates into non-overlapping players, sub-questions, or source classes. Fan-out buys breadth, not depth on one thread. At `high`, legs may run in parallel.

Brief each worker with the exact gap, boundaries, source tiers, frontier posture, and expected output, and require structured findings with direct citations, uncertainty, and unresolved gaps. Carry the citations and material detail into synthesis. Workers share any session-wide search cap. Keep decisions about what to chase next and how to weigh evidence with the primary researcher. Keep fan-out one level deep: workers do not re-delegate, because each handoff layer drops findings.

A permitted cross-model worker may also take a closed-ended leg, such as version checks or a known list of contested claims, under the same scope, citation, budget, and authorization rules.

## Independent cross-model sweep

At `high`, or at `med` for a decision the user will act on, launch a background sweep of the full question **at probe time**, when permitted. Use an installed, authenticated engine from a **different model family**: Claude primary → Codex/GPT; Codex/GPT primary → Claude. A same-family rerun is not triangulation. Skip silently for pure lookups, `low`, or when no independent engine is available. Do not install or authenticate an engine to force a sweep.

Claude primary → Codex (pin chosen 2026-09-30 from a same-prompt medium/high comparison in [evidence.md](evidence.md)):

```sh
codex exec -s read-only -c 'web_search="live"' \
  -m gpt-6.1-sol -c model_reasoning_effort=high --skip-git-repo-check --json \
  --output-last-message <scratchpad>/codex-sweep-$(date +%s).md \
  "<question + frontier signal posture>" </dev/null
```

Codex primary → Claude (web tools must be allowed explicitly; checked on Claude Code 2.1.285):

```sh
claude -p "<question + frontier signal posture>" --model opus \
  --allowedTools "WebSearch,WebFetch" </dev/null > <scratchpad>/claude-sweep-$(date +%s).md
```

Keep the prompt before `--allowedTools`, which takes a variable-length list. The `opus` alias tracks the current Opus; Bedrock, Vertex, and Foundry may map it to an older build, and WebSearch is unavailable on Bedrock.

Use a unique output path and reject a sweep file whose modification time predates launch. Headless runs of either CLI can bill without a consent prompt; use only existing authorization.

### Choosing or replacing the pin

Model lineups change monthly; confirm an ID is live before use (Codex: `~/.codex/models_cache.json`; Claude: the model list of the installed CLI). Snapshot 2026-09-30, codex-cli 0.159.2, Claude Code 2.1.285:

- **Always pin model and effort.** An unpinned `codex exec` runs the catalog's top-ranked model at its default effort, which the local catalog lists as `low` for `gpt-6.1-sol` (the [API model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol) says `medium`).
- **Codex:** `gpt-6.1-sol` is the workhorse; `gpt-6-sol` is the previous generation. `gpt-6-astra` costs roughly 5× as much; reserve it for a hard judgment. `gpt-6-luna` and older `gpt-5.6-*` models fit enumerable lookups, not a synthesis sweep. There is no bare `gpt-5.6` slug. Never pin `gpt-5.5` (legacy) or `gpt-reserve` (hidden). Skip the `ultra` effort, which delegates automatically.
- **Claude:** prefer `opus`. A Fable-tier sweep bills usage credits silently in `-p` mode; use it only when the question demands it. Haiku is too weak for a rigorous sweep.
- **Codex flags:** `web_search` accepts `disabled`, `cached`, `indexed`, `live`; only `live` reflects current state. `--search` is a top-level flag, not an `exec` flag.

## Using the sweep

Run the main loop while the sweep works. At synthesis, compare the tracks:

- **Agreement:** raise confidence only for independent evidence and cite it once. Model agreement over the same origin is not corroboration.
- **New lead:** fetch and verify it before using it as support. A sweep URL or figure is not verified because another model supplied it. At cap, keep useful leads labeled unverified.
- **Disagreement:** prioritize primary-source verification in the draft fact-check. If it stays unresolved within budget, report the split with both sources and state access or verification limits.

The main researcher's synthesis is the answer; the sweep is a check, not a second author. Its background work does not use the main loop's rounds, but shared tool caps still apply. Different models can share errors, and neither model's output substitutes for reading the source.
