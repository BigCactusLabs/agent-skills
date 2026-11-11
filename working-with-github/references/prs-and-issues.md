# PRs, issues, and discussions

API conventions: [CLI/API](cli-and-api.md).

## Worktrees and cleanup

`gh pr checkout <PR> --worktree <path>` and `gh issue develop <issue> --checkout --worktree <path>` reject non-empty targets before branch creation and reuse existing linked worktrees. `gh repo sync` refuses branches checked out elsewhere.

Check merged state before authorized branch deletion. `gh pr merge --delete-branch` still deletes the remote branch when dirty local cleanup is skipped. For stacked PRs, read [Stacks](stacks.md).

## Reviews

Read `gh pr view --json reviewDecision,latestReviews,reviews` and inspect author logins and review bodies. Copilot (`copilot-pull-request-reviewer`) can count toward required approval in opted-in repos; new commits dismiss its approval. `APPROVED` does not prove human approval.

Copilot overview findings may have no inline comment. Rereviews can auto-resolve threads, including “Won't Fix”/“Incorrect”; refresh state and verify fixes independently of resolution.

PR JSON has no `reviewThreads`. REST `repos/OWNER/REPO/pulls/NUMBER/comments --paginate` gives line comments; for thread IDs/state, select inside GraphQL `repository { pullRequest(number: $number) { ... } }` with `$endCursor: String`:

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

Paginate each nested `comments` connection by thread ID and its own cursor. Authorized `resolveReviewThread` / `unresolveReviewThread` takes `threadId`; re-query `isResolved` afterward.

## Missing objects

PRs/issues share numbers: on failed views, query both `repos/OWNER/REPO/pulls/NUMBER` and `repos/OWNER/REPO/issues/NUMBER` with `gh api --include` to distinguish type, redirects, access, and deletion.

Admin-archived PRs are closed/locked but return 404 to non-admins. Check admin access or `is:archived` search; the audited CLI lacks an archived PR JSON field/`--state archived`.

Discussion JSON omits full thread pagination; use GraphQL for complete threads/unexposed fields. If unavailable, check repository `hasDiscussionsEnabled`.

## Attachments

`--attach <path>[#alt text]` requires push access and explicit intent; GHES is unsupported. Check command help and account upload limits; Free-plan video limits can be lower than the CLI cap. Videos have no alt text.

With `--body-file`, matching local image references become uploaded URLs with their alt text; unmatched files append. Partial upload failure can create the object with successful files, print its URL, and exit nonzero. Inspect that object before retrying to avoid duplicates.
