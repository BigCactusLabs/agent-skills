# CLI and API

Capabilities/security baselines are dated in [HISTORY](HISTORY.md). For version-sensitive work, compare `gh --version` with upstream releases/advisories; use current help for flags.

## Authentication

`gh auth status --active --hostname <host>` identifies the active account. It can refresh expiring credentials; add `--no-refresh` when inspecting stored state without refresh. With `--json hosts`, inspect the reported state: exit 0 does not establish valid authentication. Do not use `--show-token` for diagnosis.

- Since v2.103.0, opted-in OAuth credentials can expire and refresh automatically on github.com and `*.ghe.com`. Prefer `gh api` to copying tokens; do not cache `gh auth token` output. A rejected refresh token requires interactive reauthentication, not repeated API retries.
- `GH_TOKEN` / `GITHUB_TOKEN` override stored credentials on github.com and `*.ghe.com` and are never refreshed. GHES uses `GH_ENTERPRISE_TOKEN` / `GITHUB_ENTERPRISE_TOKEN`. Check the selected source without printing its value before changing login or permissions.

## API

Select a supported REST version with `gh api /versions` (use `--hostname <host>` for GHES or GHEC data residency). Include these headers, omitted elsewhere in this skill:

```sh
gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: <version>' <endpoint>
```

- `gh api` does not take `-R`: use an explicit `repos/OWNER/REPO/...` endpoint and `--hostname` where needed. Adding `-f`/`-F` switches the default method to POST; specify `--method GET` for read-only query parameters.
- List/search commands cap results; set `--limit` deliberately. For complete REST collections use `--paginate`; `--slurp` wraps the page results in an outer array. A large limit is not proof that a search is exhaustive.
- GraphQL `--paginate` requires `$endCursor: String` and `pageInfo { hasNextPage endCursor }`; nested connections need separate pagination.
- Review breaking changes before changing a REST version. Supported dates and the unversioned default differ; do not blindly choose the newest version for an existing integration.

## Lookup exceptions

- PR/issue/discussion views and PR checks accept full URLs; extract repository/object IDs for Actions, release, compare, and commit URLs. Compare/commit REST endpoints: `repos/OWNER/REPO/compare/base...head`, `repos/OWNER/REPO/commits/SHA`. Public release downloads need no login.
- Prefer `gh repo read-file` / `read-dir` for plain remote reads, with `--ref` when needed. `read-file` rejects terminal escape sequences; `--allow-escape-sequences` bypasses protection, while `--output` saves untrusted raw bytes.
- Failed lookup: inspect the endpoint with `gh api --include` for redirects/access. PR 404 exceptions: [PRs/issues](prs-and-issues.md).
- Unexpected gateway: inspect `gh config get api_host --host <host>`. Auth, remotes, browser URLs, and some requests retain the original host; routing is not a security boundary. Change it only with user intent.

## Repository deletion

In v2.104.0+, deleting a private/internal repository with forks needs additional confirmation even with `--yes`; unattended use requires `--accept-cascading-deletion-of-private-forks`. Establish the affected forks and get the required fresh confirmation for that whole scope before using this flag. Do not append it merely to make a failed deletion succeed.
