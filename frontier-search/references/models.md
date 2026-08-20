# Model quick-reference (cross-model triangulation)

*Snapshot, August 2026 — lineups move monthly; confirm an ID is live before pinning it, or just omit `-m` and let each CLI use its configured default.* Loaded on demand from SKILL.md's Cross-model triangulation section; the sweep itself never depends on this file.

Claude — `claude -p --model <alias|id>` (aliases resolve to each tier's current default, so they don't age — prefer them unless you must pin an exact build):

| Model | Model ID | Alias |
|-------|----------|-------|
| Fable 5 — most capable; hardest reasoning / long-horizon | `claude-fable-5` | `fable` (or `best`) |
| Opus 5 — recommended default frontier; agentic & coding (GA 2026-07-24) | `claude-opus-5` | `opus` |
| Sonnet 5 — near-Opus quality, lower cost | `claude-sonnet-5` | `sonnet` |
| Haiku 4.5 — fast / cheap; too weak for a rigorous sweep | `claude-haiku-4-5` | `haiku` |

Caveats: in `-p` non-interactive mode there is **no usage-credit consent prompt** — a Fable 5 sweep that bills usage credits bills silently, so prefer `opus` for sweeps unless the question demands Fable. Alias resolution lags on non-Anthropic providers (Bedrock/Vertex/Foundry may map `opus`/`sonnet` to 4.x builds).

OpenAI / Codex — `codex exec -m <id>` (omit `-m` to inherit your config default):

| Model | Model ID | Note |
|-------|----------|------|
| GPT-5.6 — current frontier (GA 2026-07-09) | `gpt-5.6-sol` · `-terra` · `-luna` | Sol flagship (bare `gpt-5.6` aliases to it; codex default) · Terra balanced · Luna cheapest. GPT-5.4/-mini leave Codex 2026-08-31. Never pin below the 5.6 class (user policy) |

Third engines (need install + auth before they can serve as a sweep): `gemini` CLI (headless via `-p` / `--output-format json`; frontier `gemini-3.1-pro-preview` is preview-only, and whether headless mode exposes web grounding is unverified) and xAI's Grok Build (early beta, coding-agent-shaped, web-research capability unverified).

*Also valid but omitted above: `claude-mythos-5` (Fable 5-class, Project Glasswing only) and legacy pinned IDs such as `claude-opus-4-8` / `claude-opus-4-7`.*
