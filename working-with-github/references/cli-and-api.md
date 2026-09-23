# CLI and API

## Version-sensitive behavior

September 19, 2026 audit: installed and upstream latest `gh` were v2.101.0. Recheck `gh --version` and `gh release view -R cli/cli --json tagName,publishedAt,url` when version matters. The recorded security fixes require v2.98.0 or newer; prefer the current release and check `gh api repos/cli/cli/security-advisories`. Sources: [HISTORY.md](HISTORY.md).

`gh discussion`, `gh agent-task`, `gh skill`, and remote file reads were preview at that baseline. Verify help before use.

## REST and GraphQL

GitHub.com supported REST versions `2026-03-10` and `2022-11-28` at the audit; unversioned calls defaulted to the latter. For GitHub.com/GHEC REST fallbacks, use these headers unless testing older compatibility:

```sh
gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' <endpoint>
```

Verify with `gh api /versions`; for GHES or GHEC data residency, use `gh api --hostname <host> /versions` before selecting a version. Other references omit these shared headers from examples; include them when executing.

For GraphQL `gh api --paginate`, declare `$endCursor: String` and request `pageInfo { hasNextPage endCursor }`. Paginate nested connections separately.

## Object lookup

Full URLs work with `gh pr view`, `gh issue view`, `gh pr checks`, and `gh discussion view`. Parse Actions, release, compare, and commit URLs into repository and object IDs. Append `-R owner/repo` where needed.

| Object | Inspection |
| --- | --- |
| PR / issue / discussion | `gh pr view <url>` / `gh issue view <url>` / `gh discussion view <url>` |
| PR diff | `gh pr diff <number-or-url> --patch` |
| Release | `gh release view <tag>`; omit tag for latest |
| Release assets | `gh release download <tag>`; public downloads need no login (v2.96+) |
| Compare | `gh api repos/OWNER/REPO/compare/base...head` |
| Commit | Local `git show <sha>`; otherwise `gh api repos/OWNER/REPO/commits/SHA` |
| Repository | `gh repo view OWNER/REPO` |
| Remote file / directory | `gh repo read-file <path>` / `gh repo read-dir [<path>]`, with optional `--ref <branch\|tag\|sha>` |

Prefer remote file commands for plain reads; private repos and GHES are supported. `read-file` rejects escape sequences in terminal/piped output. `--allow-escape-sequences` bypasses protection; `--output` saves raw bytes. Treat saved content as untrusted.

If object view fails, inspect its API endpoint with `--include` for redirects or access limits. A PR 404 can mean admin-only archival; see [prs-and-issues.md](prs-and-issues.md).

For unexpected gateways, inspect `gh config get api_host --host <host>` (v2.100+). Experimental routing leaves authentication, Git remotes, and browser URLs on the original host; some requests still reach it. It is not a security boundary. Do not change routing without user intent.
