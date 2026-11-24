# PRs, issues, and discussions

API conventions: [CLI/API](cli-and-api.md).

## Creation and merging

`gh pr create --dry-run` can still push.

Authorized merge: read the current `headRefOid`, reviews, and checks, then `gh pr merge --match-head-commit <SHA>`; refresh if the head moves. On merge-queue branches the command enables auto-merge or queues the PR, so verify the final merged state. `--admin` bypasses requirements and needs explicit intent. Stacked PRs: [Stacks](stacks.md).

## Worktrees and cleanup

`gh pr checkout <PR> --worktree <path>` and `gh issue develop <issue> --checkout --worktree <path>` reject non-empty targets and reuse existing linked worktrees. `gh repo sync` refuses branches checked out elsewhere.

`gh pr merge --delete-branch` deletes the remote branch even when dirty local cleanup is skipped.

## Reviews

Read `gh pr view --json reviewDecision,latestReviews,reviews` and check author logins. Copilot (`copilot-pull-request-reviewer`) can count toward required approval in opted-in repos, so `APPROVED` does not prove human approval; new commits dismiss its approval. Its overview findings may have no inline comment, and rereviews can auto-resolve threads (including "Won't Fix"/"Incorrect"); verify fixes independently.

PR JSON has no `reviewThreads`. Line comments: REST `repos/OWNER/REPO/pulls/NUMBER/comments --paginate`. Thread IDs/state: GraphQL under `repository { pullRequest(number: $number) { ... } }` with `$endCursor: String`:

```graphql
reviewThreads(first: 100, after: $endCursor) {
  nodes {
    id isResolved isOutdated path line
    comments(first: 20) {
      nodes { author { login } body url }
      pageInfo { hasNextPage endCursor }
    }
  }
  pageInfo { hasNextPage endCursor }
}
```

Paginate each nested `comments` by thread ID. Authorized `resolveReviewThread` / `unresolveReviewThread` take `threadId`; re-query `isResolved` after.

## Waiting for events

`gh event listen --resource <PR-URL> --event <type>[,<type>] --timeout 30m` (v2.105.0+, preview; enrolled github.com accounts only) waits for a PR change instead of polling. Types under `com.github.pull_request.`: `review.submitted.v1`, `state.changed.v1`, `head.changed.v1`, `merge_conflict.v1`, `check_suite.status.changed.v1`.

- Exits after one event (`--count`, `--follow`); timeout exits 8. Fetch `data.api_url` for what changed.
- Nothing is replayed: read PR state once attached and after any reconnect.
- Each check suite sends its own event; confirm all checks with `gh pr checks`.
- Listening creates or reuses a subscription (24 h expiry, per-account limit; `gh event subscription list`).

## Missing objects

PRs and issues share numbers: query both `repos/OWNER/REPO/pulls/NUMBER` and `.../issues/NUMBER` with `gh api --include` to tell type, redirect, access, or deletion apart.

Admin-archived PRs are closed/locked and 404 for non-admins; check admin access or `is:archived` search (the CLI has no archived field or `--state archived`).

Discussion JSON omits full threads; use GraphQL. If missing, check repository `hasDiscussionsEnabled`.

## Attachments

`--attach <path>[#alt text]` (not on GHES) needs push access and explicit intent. Body references to an attached file become uploaded URLs; unmatched files are appended. With `--body-file`, relative paths resolve against the body file's directory, then the working directory. A partial upload failure can still create the object and exit nonzero: inspect it before retrying. The upload endpoint refuses some GitHub App tokens.
