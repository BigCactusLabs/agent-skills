# CLI and API

Dated baselines: [HISTORY](HISTORY.md). For version-sensitive work, compare `gh --version` with upstream releases; check current help for flags.

## Authentication

`gh auth status --active --hostname <host>` shows the active account and may refresh credentials; add `--no-refresh` to inspect stored state. With `--json hosts`, read the reported state: exit 0 does not prove valid auth. Never use `--show-token` for diagnosis.

- v2.103.0+: opted-in OAuth credentials can expire and auto-refresh (github.com, `*.ghe.com`). Use `gh api` rather than copying or caching `gh auth token`. A rejected refresh token needs interactive reauth, not retries.
- `GH_TOKEN`/`GITHUB_TOKEN` (GHES: `GH_ENTERPRISE_TOKEN`/`GITHUB_ENTERPRISE_TOKEN`) override stored credentials and never refresh. Check which source is active, without printing it, before changing login or permissions.

## API

Pick a supported REST version from `gh api /versions` (`--hostname <host>` for GHES/data residency); review breaking changes before moving an integration to a newer one. Headers, omitted elsewhere in this skill:

```sh
gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: <version>' <endpoint>
```

- `gh api` has no `-R`: use `repos/OWNER/REPO/...` and `--hostname`. `-f`/`-F` switch the method to POST; add `--method GET` for read queries.
- List/search commands cap results; set `--limit` deliberately. `--paginate` for full REST collections; `--slurp` wraps pages in one array.
- GraphQL `--paginate` needs `$endCursor: String` and `pageInfo { hasNextPage endCursor }`; paginate nested connections separately.

## Lookups

- PR/issue/discussion views and `pr checks` accept URLs; for Actions, release, compare, and commit URLs, extract IDs (`repos/OWNER/REPO/compare/base...head`, `.../commits/SHA`).
- Remote files: `gh repo read-file` / `read-dir` (`--ref`). `read-file` rejects terminal escapes unless `--allow-escape-sequences`; `--output` saves raw untrusted bytes.
- Failed lookup: `gh api --include` shows redirects/access. PR 404s: [PRs/issues](prs-and-issues.md#missing-objects).
- Unexpected gateway: check `gh config get api_host --host <host>`. It is not a security boundary; change it only on user intent.

## Repository deletion

v2.104.0+: deleting a private/internal repo with forks needs `--accept-cascading-deletion-of-private-forks` even with `--yes`. Identify the forks and get fresh confirmation for that whole scope first; never add the flag just to make a failed delete pass.
