# PRs, issues, and discussions

API conventions: [CLI/API](cli-and-api.md).

## Creation and merging

`gh pr create --dry-run` may still push Git changes. For a local-only preview, prepare the title/body in a file and inspect the diff.

For an authorized ordinary PR merge, read the current `headRefOid`, review state, and checks, then pass that verified SHA to `gh pr merge --match-head-commit <SHA>`. If the head changes, refresh the evidence. On a merge-queue branch, the command enables auto-merge while checks are pending or queues the PR when ready; verify the eventual merged state before reporting completion. `--admin` bypasses requirements and needs explicit intent. For stacked PRs use [Stacks](stacks.md).

### Async merge API

For custom merge automation or CLI gaps, GitHub recommends the [async merge API](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request-asynchronously). Use `gh api --method PUT repos/OWNER/REPO/pulls/NUMBER/merge-async`, with the API headers from [CLI/API](cli-and-api.md) and a structured JSON payload via `--input`. Set `sha` to the verified head, use `merge_action: "default"` to respect the configured queue, and leave `bypass_rules` false unless explicitly authorized. For a stacked PR, the request includes all open PRs below it; verify that whole scope first.

- `202` accepts a background request; retain its UUID. `409` returns an existing pending request and its options: inspect those before tracking it instead of submitting again. Acceptance checks basic PR state; branch rules are evaluated during processing.
- Poll `GET repos/OWNER/REPO/pulls/NUMBER/merge-async/UUID` with bounded waits. `pending` is unfinished; `failed` includes the reason; `merged` includes the merge commit SHA. `enqueued` is a terminal result for this API request, so switch to checking the PR's eventual merge state.
- Results expire 24 hours after their last update. On a timeout, connection failure, or expired UUID, inspect the PR and queue state before retrying. Report a still-pending operation as pending, not complete.

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

With `--body-file`, relative attachment paths and Markdown destinations resolve against the body file's directory first, then the working directory. Matching local image references become uploaded URLs with their alt text; unmatched files append. Partial upload failure can create the object with successful files, print its URL, and exit nonzero. Inspect that object before retrying to avoid duplicates. Current clients defer token eligibility to the upload endpoint; some GitHub App tokens are accepted, others are refused even with write access.

## Issue artifacts

`gh issue artifact` (v2.103.0+, private preview at audit) manages documents and links attached to issues. Use `list`/`view` to inspect them; Actions artifacts use `gh run download`. Command availability does not imply repository enrollment.

Batch `create` can partially succeed and exit 1; inspect its per-item results and retry only failed items. `edit --restore-version N` saves a new version; it does not erase history. Confirm the issue, artifact, and requested change before mutations.
