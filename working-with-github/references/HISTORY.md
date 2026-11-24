# Audit evidence

Dated evidence, not current guarantees. Recheck releases/help before capability decisions.

## November 20, 2026

CLI v2.105.0 installed (latest). gh-stack v0.3.0 unchanged; gh-aw v1.3.1 and gh-actions-lock v0.5.1 source-checked, not installed. Help and read-only API only; no event subscription created. November 12 CLI rows rechecked against help (issue 14371 still open); changelog rows not rechecked.

| Finding | Evidence |
| --- | --- |
| v2.105.0 `gh event listen` / `subscription` (preview, github.com only); no replay, timeout exits 8 | [release](https://github.com/cli/cli/releases/tag/v2.105.0), [announcement](https://github.blog/changelog/2026-11-17-github-event-streams-is-now-in-preview) |
| gh-actions-lock v0.5.0 `--fail-on-warning`; never writes action files; exact lock key for full-SHA uses | [v0.5.0](https://github.com/github/gh-actions-lock/releases/tag/v0.5.0), [README](https://github.com/github/gh-actions-lock/blob/v0.5.1/README.md) |
| gh-aw v1.2.3-v1.3.1 breaking defaults: fork admission, protected-file merges, checksum pins, model routing, connectors, MCP write tools | [v1.3.0](https://github.com/github/gh-aw/releases/tag/v1.3.0), [v1.3.1](https://github.com/github/gh-aw/releases/tag/v1.3.1) |

## November 12, 2026

CLI v2.103.3 installed, v2.104.0 upstream; gh-stack v0.3.0 and gh-aw v1.2.2 source-checked, not installed. Read-only API and help checks only.

| Finding | Evidence |
| --- | --- |
| v2.103.0 expiring credentials, issue artifacts; env tokens don't refresh | [release](https://github.com/cli/cli/releases/tag/v2.103.0) |
| v2.103.2 attachment token eligibility decided server-side | [release](https://github.com/cli/cli/releases/tag/v2.103.2) |
| v2.104.0 cascading private-fork deletion flag | [release](https://github.com/cli/cli/releases/tag/v2.104.0) |
| Queued rerun can show stale pass (still open) | [issue](https://github.com/cli/cli/issues/14371) |
| REST versions `2026-03-10`, `2022-11-28` (default; support ends March 10, 2028) | [policy](https://docs.github.com/en/rest/about-the-rest-api/api-versions) |
| `pull_request_target` public-repo block from December 2 | [changelog](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2/) |
| Retention covers checks/runs/statuses | [changelog](https://github.blog/changelog/2026-10-01-actions-retention-now-covers-checks-runs-and-statuses/) |
| Actions lockfiles GA | [changelog](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/) |
| Stacked PRs GA; trunk rules; approvals kept on unchanged rebases | [changelog](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/), [reference](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests) |
| gh-stack v0.3.0 atomic push; base-change acceptance; sync can exit 0 incomplete | [release](https://github.com/github/gh-stack/releases/tag/v0.3.0), [sync source](https://github.com/github/gh-stack/blob/v0.3.0/cmd/sync.go) |
| Agentic Workflows GA; forecast; `--no-emit` caches | [changelog](https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/) |
| Async merge API GA | [changelog](https://github.blog/changelog/2026-10-01-github-async-merge-api-generally-available/) |

Counter-check: the v0.3.0 stack README says queued stacks may land in separate groups; server docs say they stay together. Verify final PR states.
