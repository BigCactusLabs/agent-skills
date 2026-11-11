# CLI and API

Capabilities/security baselines are dated in [HISTORY](HISTORY.md). For version-sensitive work, compare `gh --version` with upstream releases/advisories; use current help for flags.

## API

Select a supported REST version with `gh api /versions` (use `--hostname <host>` for GHES or GHEC data residency). Include these headers, omitted elsewhere in this skill:

```sh
gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: <version>' <endpoint>
```

GraphQL `--paginate` requires `$endCursor: String` and `pageInfo { hasNextPage endCursor }`; nested connections need separate pagination.

## Lookup exceptions

- PR/issue/discussion views and PR checks accept full URLs; extract repository/object IDs for Actions, release, compare, and commit URLs. Compare/commit REST endpoints: `repos/OWNER/REPO/compare/base...head`, `repos/OWNER/REPO/commits/SHA`. Public release downloads need no login.
- Prefer `gh repo read-file` / `read-dir` for plain remote reads, with `--ref` when needed. `read-file` rejects terminal escape sequences; `--allow-escape-sequences` bypasses protection, while `--output` saves untrusted raw bytes.
- Failed lookup: inspect the endpoint with `gh api --include` for redirects/access. PR 404 exceptions: [PRs/issues](prs-and-issues.md).
- Unexpected gateway: inspect `gh config get api_host --host <host>`. Auth, remotes, browser URLs, and some requests retain the original host; routing is not a security boundary. Change it only with user intent.
