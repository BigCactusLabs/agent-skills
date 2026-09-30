# Claude Code search and fetch behavior

Claude Code specifics for `WebSearch` / `WebFetch`; other runtimes have their own contracts. Snapshot verified 2026-09-30 (Claude Code 2.1.285); sources and version qualifiers are in [evidence.md](evidence.md#runtime-facts).

- **Search:** US-only; returns title/URL blocks and may run up to eight backend searches per call. `allowed_domains` and `blocked_domains` cannot be combined in one call.
- **Shared cap:** 200 searches per session by default, subagents included. `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` raises it; `/clear` resets it unless a workflow survives the clear. A capped call can look like an empty result: follow the cap notice, do not infer thin evidence, and do not raise the limit silently.
- **Extraction:** `WebFetch` returns a small model's answer to your prompt, not the page. Before treating silence on a claim as evidence, ask a sharper question. Large pages are truncated before extraction; if the section you need is missing, fetch the raw page with `curl`. The extractor can misattribute detail (such as which release a changelog entry belongs to), so take exact versions, dates, and figures from the raw page.
- **Cache:** 15 minutes per URL by default; re-fetching within that window will not show recent edits.
- **Redirects:** cross-host redirects are returned, not followed. Fetch the destination, and distinguish a moved source from a dead one.
- **Blocked hosts:** WebFetch checks each hostname against an Anthropic safety blocklist; Reddit has been refused. A refusal is a tool decision, not evidence the site is down. Before v2.1.285 a rate-limited check could be reported as a network or policy block, so retry once before recording one. WebFetch sends a `Claude-User` user agent and asks for Markdown; a host that rejects it may still answer `curl`. Some registries need APIs and some venues need subscriptions (see [sources.md](sources.md)). Snippets and APIs can supply leads; a decision-relevant claim stays `Access-limited:` until accessible evidence verifies it.
- **Availability:** WebFetch can be switched off (`CLAUDE_CODE_DISABLE_WEB_FETCH`, v2.1.285) or withheld in Team and Enterprise sessions until organization policy loads. WebSearch is unavailable on Amazon Bedrock and on Azure-hosted Microsoft Foundry deployments. Report a missing tool as an access limit and use whatever retrieval route remains.

For direct HTTP requests, set the user agent to `OpenAI File Downloader, XaiImageApiFetch/1.0`.
