# Model quick-reference (cross-model triangulation)

*Snapshot, 2026-09-02; OpenAI section re-verified against the live Codex catalog on 2026-09-06; Claude `opus` alias re-checked 2026-09-23 (resolves to `claude-opus-5-5` on claude-code 2.1.280) — lineups move monthly; confirm an ID is live before pinning it; always pass a model flag, since an unpinned Codex dispatch runs the server catalog's top-ranked model at its own default effort.* Consult from [parallel-research.md](parallel-research.md) when selecting or replacing a sweep model; that guide carries the default command and pin.

Claude — `claude -p --model <alias|id>` (aliases resolve to each tier's current default, so they don't age — prefer them unless you must pin an exact build):

| Model | Model ID | Alias |
|-------|----------|-------|
| Fable 5.1 — most capable widely released; hardest reasoning / long-horizon (successor to Fable 5, same price tier) | `claude-fable-5-1` | `fable` |
| Opus 5.5 — recommended default frontier; agentic & coding (successor to Opus 5, lower price) | `claude-opus-5-5` | `opus` |
| Sonnet 5 — near-Opus quality, lower cost | `claude-sonnet-5` | `sonnet` |
| Haiku 4.5 — fast / cheap; too weak for a rigorous sweep | `claude-haiku-4-5` | `haiku` |

Caveats: in `-p` non-interactive mode there is **no usage-credit consent prompt** — a Fable-tier sweep that bills usage credits bills silently, so prefer `opus` for sweeps unless the question demands Fable. Fable 5.1 rejects forced `tool_choice` and needs 30-day data retention; neither matters for a `-p` sweep. Alias resolution lags on non-Anthropic providers (Bedrock/Vertex/Foundry may map `opus`/`sonnet` to 4.x builds). `claude-opus-5`, `claude-fable-5`, and `claude-opus-4-8` are still served if an older pin is needed.

OpenAI / Codex — `codex exec -m <id> -c model_reasoning_effort=<effort>` (always pin both: an unpinned dispatch runs the server catalog's top-ranked model at that model's own default effort):

| Model | Model ID | Note |
|-------|----------|------|
| GPT-6 Astra — current frontier (released 2026-09-03); single variant, no cheap tier | `gpt-6-astra` | Tops the server catalog (`~/.codex/models_cache.json`, priority 1), so it is what an unpinned run gets, at its `medium` default. Judge / hard-repair tier only in the orchestrator's ladder: never a bulk sweep (ChatGPT per-message quota ≈ 1/50 luna). Not offered in Codex cloud. CLI context 272K (API 1.05M; the whole request reprices above 272K input) |
| GPT-5.6 (GA 2026-07-09) | `gpt-5.6-sol` · `-terra` · `-luna` | **No bare `gpt-5.6` slug exists** — always the full id. Terra @ `max` is the sweep pin in parallel-research.md; luna @ `max` for enumerable lookups; sol is off the orchestrator's ladder (user decision) and serves only as the Codex-cloud fallback where astra isn't offered. Catalog default efforts (sol `low`, terra and luna `medium`) are the wrong dial for a sweep — pin effort explicitly |
| Below the 5.6 class | `gpt-5.5` · `gpt-5.4-mini` · `gpt-5.3-codex-spark` | Still listed in the catalog as of this snapshot; never a pin target (user policy) |

Codex exec facts that matter for the sweep command (re-verified on codex-cli 0.153.4, 2026-09-06): `web_search` accepts `disabled`, `cached`, `indexed`, `live`, so `-c web_search="live"` is the right way to force live search under `exec` — `--search` is a top-level TUI flag, not an `exec` flag, and the boolean `tools.web_search=true` deserializes but is silently ignored. `-s read-only`, `--skip-git-repo-check`, `--json` (JSONL events to stdout), and `-o/--output-last-message <FILE>` are all current.

Third engines (need install + auth before they can serve as a sweep; neither is installed on this machine as of the snapshot):

- **Gemini CLI** — headless via `-p` / `--output-format json|stream-json`. Current GA frontier is `gemini-3.8-flash` (GA 2026-09-02); the Pro tier is `gemini-3.1-pro-preview` and still preview. The README lists Google Search grounding as built in, but the headless doc is silent on whether it is on under `-p` — verify with one run before trusting a Gemini sweep for web research.
- **xAI Grok Build** — headless coding agent that searches the web (`grok -p <prompt> --output-format json`, model `grok-4.6`). Only status statement found is "early beta" (2026-05-25); web-research quality unverified.

*Also valid but omitted above: `claude-mythos-5-1` (Fable 5.1-class, Project Glasswing only) and legacy pinned IDs such as `claude-opus-4-7`.*
