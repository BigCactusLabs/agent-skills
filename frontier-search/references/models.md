# Model quick-reference (cross-model triangulation)

*Snapshot, 2026-09-02 — lineups move monthly; confirm an ID is live before pinning it, or just omit the model flag and let each CLI use its configured default.* Loaded on demand from SKILL.md's Cross-model triangulation section; the sweep itself never depends on this file.

Claude — `claude -p --model <alias|id>` (aliases resolve to each tier's current default, so they don't age — prefer them unless you must pin an exact build):

| Model | Model ID | Alias |
|-------|----------|-------|
| Fable 5.1 — most capable widely released; hardest reasoning / long-horizon (successor to Fable 5, same price tier) | `claude-fable-5-1` | `fable` |
| Opus 5 — recommended default frontier; agentic & coding | `claude-opus-5` | `opus` |
| Sonnet 5 — near-Opus quality, lower cost | `claude-sonnet-5` | `sonnet` |
| Haiku 4.5 — fast / cheap; too weak for a rigorous sweep | `claude-haiku-4-5` | `haiku` |

Caveats: in `-p` non-interactive mode there is **no usage-credit consent prompt** — a Fable-tier sweep that bills usage credits bills silently, so prefer `opus` for sweeps unless the question demands Fable. Fable 5.1 rejects forced `tool_choice` and needs 30-day data retention; neither matters for a `-p` sweep. Alias resolution lags on non-Anthropic providers (Bedrock/Vertex/Foundry may map `opus`/`sonnet` to 4.x builds). `claude-fable-5` and `claude-opus-4-8` are still served if an older pin is needed.

OpenAI / Codex — `codex exec -m <id>` (omit `-m` to inherit your config default):

| Model | Model ID | Note |
|-------|----------|------|
| GPT-5.6 — current frontier (GA 2026-07-09; nothing newer listed as of this snapshot) | `gpt-5.6-sol` · `-terra` · `-luna` | Sol flagship (bare `gpt-5.6` aliases to it; codex default) · Terra balanced · Luna cheapest. GPT-5.4/-mini were announced to retire from Codex for ChatGPT sign-in on 2026-08-31 but still appear in the model catalog fetched today — treat them as retiring, not as a pin target. Never pin below the 5.6 class (user policy) |

Codex exec facts that matter for the sweep command (verified on codex-cli 0.152.1): `web_search` accepts `cached` (default), `indexed`, `live`, `disabled`, so `-c 'web_search="live"'` is the right way to force live search under `exec` — the `--search` flag exists only on the interactive TUI and is not an `exec` flag. `-s read-only`, `--json` (JSONL events to stdout), and `-o/--output-last-message <FILE>` are all current.

Third engines (need install + auth before they can serve as a sweep; neither is installed on this machine as of the snapshot):

- **Gemini CLI** — headless via `-p` / `--output-format json|stream-json`. Current GA frontier is `gemini-3.8-flash` (GA 2026-09-02); the Pro tier is `gemini-3.1-pro-preview` and still preview. The README lists Google Search grounding as built in, but the headless doc is silent on whether it is on under `-p` — verify with one run before trusting a Gemini sweep for web research.
- **xAI Grok Build** — headless coding agent that searches the web (`grok -p <prompt> --output-format json`, model `grok-4.6`). Only status statement found is "early beta" (2026-05-25); web-research quality unverified.

*Also valid but omitted above: `claude-mythos-5-1` (Fable 5.1-class, Project Glasswing only) and legacy pinned IDs such as `claude-opus-4-7`.*
