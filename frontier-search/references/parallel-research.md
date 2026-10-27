# Parallel research and cross-model checks

Read when considering a probe-time sweep or disjoint research legs. Runtime policy and user authorization govern subagents and external research CLIs; when either is restricted, work inline without a warning or degraded-status footer. `low` disables both.

## Disjoint research legs

At `med`/`high`, dispatch only when a gap needs >2 fetches and >1 search **and** separates into non-overlapping players, sub-questions, or source classes. Fan-out buys breadth, not depth on one thread. At `high`, legs may run in parallel.

Brief each worker with the exact gap, boundaries, source tiers, frontier posture, and expected output; require structured findings with direct citations, uncertainty, and open gaps, and carry those into synthesis. Workers share any session-wide search cap. The primary researcher decides what to chase next and how to weigh evidence. Fan-out stays one level deep: workers do not re-delegate, because each handoff drops findings.

A permitted cross-model worker may also take a closed-ended leg, such as version checks or a known list of contested claims, under the same scope, citation, budget, and authorization rules.

## Independent cross-model sweep

At `high`, or `med` for a decision the user will act on, launch a background sweep of the full question **at probe time**, when permitted, on an installed, authenticated engine from a **different model family** (Claude primary → Codex/GPT; Codex/GPT primary → Claude). A same-family rerun is not triangulation. Skip silently for pure lookups, `low`, or no independent engine; never install or authenticate one to force a sweep.

Claude primary → Codex (pin chosen 2026-09-30 from a same-prompt medium/high comparison in [evidence.md](evidence.md)):

```sh
codex exec -s read-only -c 'web_search="live"' \
  -m gpt-6.1-sol -c model_reasoning_effort=high --skip-git-repo-check --json \
  --output-last-message <scratchpad>/codex-sweep-$(date +%s).md \
  "<question + frontier signal posture>" </dev/null
```

Codex primary → Claude (web tools must be allowed explicitly; checked on Claude Code 2.1.311):

```sh
claude -p "<question + frontier signal posture>" --model opus \
  --allowedTools "WebSearch,WebFetch" </dev/null > <scratchpad>/claude-sweep-$(date +%s).md
```

Keep the prompt before `--allowedTools`, which takes a variable-length list. In `-p` the 200-call limit counts per run and does not refill by default (v2.1.290+), so it is hard for one sweep. The `opus` alias tracks the current Opus; Bedrock, Vertex, and Foundry may map it to an older build, and WebSearch is unavailable on Bedrock.

Use a unique output path and reject a sweep file older than its launch. Headless runs of either CLI can bill without a consent prompt; use only existing authorization.

### Choosing or replacing the pin

Lineups change monthly; confirm an ID is live first (Codex: `~/.codex/models_cache.json`; Claude: the installed CLI's model list). Snapshot 2026-09-30, re-checked 2026-10-26 (codex-cli 0.164.0, Claude Code 2.1.311; the catalog adds `gpt-6.1-terra`, and 0.163–0.164 changed no web-search behavior):

- **Always pin model and effort.** Unpinned, `codex exec` runs the catalog's top model at its default effort, listed locally as `low` for `gpt-6.1-sol` (the [API model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol) says `medium`).
- **Codex:** `gpt-6.1-sol` is the workhorse, `gpt-6-sol` the previous generation; `gpt-6-astra` (~5× cost) is for a hard judgment; `gpt-6-luna` and `gpt-5.6-*` (no bare `gpt-5.6`) fit enumerable lookups, not a sweep. Never pin `gpt-5.5` (legacy), `gpt-reserve` (hidden), or the Terra tiers (user decision 2026-10-26); skip `ultra` effort (auto-delegates).
- **Claude:** prefer `opus`. Fable-tier silently bills usage credits in `-p`; use it only when the question demands it. Haiku is too weak for a sweep.
- **Codex flags:** `web_search` accepts `disabled`, `cached`, `indexed`, `live`; only `live` reflects current state. `--search` is a top-level flag, not an `exec` flag. Pass `web_search` explicitly: since 0.161.0 implicit client settings no longer override server or saved-thread settings. Since 0.162.0 a custom provider with `external_web_access = false` keeps hosted search off the live web whatever the prompt says, so confirm a sweep searched live before treating it as a freshness check.

## Using the sweep

Run the main loop while the sweep works; it uses no rounds, but shared tool caps apply. At synthesis, the sweep is a check, not a second author: its agreement adds confidence only through independent evidence; its new leads are unverified until fetched; a disagreement gets primary-source priority in the fact-check and, if unresolved within budget, is reported with both sources. Models can share errors, and neither model's output substitutes for reading the source.
