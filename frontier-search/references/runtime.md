# Claude Code search and fetch behavior

Read before using `WebSearch` / `WebFetch`. These are Claude Code details, not assumptions about other runtimes. Snapshot verified 2026-09-22; source links and version qualifiers are in [evidence.md](evidence.md#runtime-facts).

- **Search:** US-only; returns title/URL blocks and may issue up to eight backend searches per call. `allowed_domains` and `blocked_domains` cannot be combined in one call. Use allowlists to target primaries/tiers and blocklists when a known farm or over-recurring community page dominates.
- **Shared cap:** 200 searches per session by default, including subagents. `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` raises the cap; `/clear` resets it, subject to surviving workflows. A capped call can resemble an empty result. Follow the cap notice; do not infer thin evidence or silently raise the limit.
- **Extraction:** `WebFetch` returns a small model's response to the supplied prompt, not the full page. Before treating silence on a claim as evidence, ask a sharper question. Large pages are truncated before extraction; if the relevant section is missing, fetch the raw page with `curl` through the shell.
- **Cache:** Results are cached per URL for 15 minutes by default. Re-prompting within that window reuses the cached page; recent page edits will not appear.
- **Redirects:** Cross-host redirects are returned, not followed. Fetch the returned destination; distinguish a moved source from a dead one.
- **Blocked hosts:** Reddit is refused; some registries need APIs and some venues require subscriptions. See [sources.md](sources.md). Snippets or APIs can provide leads; decision-relevant claims remain `Access-limited:` unless accessible evidence verifies them.

For direct HTTP requests, set the user agent to `OpenAI File Downloader, XaiImageApiFetch/1.0`. Do not treat tool limits or extraction omissions as facts about the topic.
