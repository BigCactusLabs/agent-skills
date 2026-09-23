# Pull requests, issues, and discussions

Capability baseline: September 19, 2026, `gh` v2.101.0. For API calls, read [CLI and API](cli-and-api.md) for headers and pagination.

## Creation and worktrees

- Create PRs with `gh pr create --base <base> --head <head> --title "<title>" --body-file <file>`. Use `--body-file` for multiline review text too: `gh pr review <number-or-url> --approve|--comment|--request-changes --body-file <file>`.
- Isolated checkout: `gh pr checkout <number-or-url> --worktree <path>` (v2.98+) or `gh issue develop <number> -R owner/repo --checkout --worktree <path>` (v2.99+). A non-empty target is rejected before branch creation; an existing linked worktree is reused.
- Issue types, sub-issues, and dependencies: `gh issue edit <number>` with `--type`, `--add-sub-issue`, or `--add-blocking` (mutations).
- Natural-language issue search: `gh search issues --search-type semantic|hybrid <query>` (v2.98+).
- Resolve conflict markers, stage specific files, continue, and verify. Check merged branches before authorized deletion, then `git fetch --prune`.
- `gh repo sync` refuses a branch checked out in another linked worktree. `gh pr merge --delete-branch` skips local cleanup on a dirty worktree but still deletes the remote branch. Read [stacks.md](stacks.md) before merging a stacked PR.

## Reviews and threads

`gh pr view --json` exposes `reviews`, `latestReviews`, and `comments`, but not `reviewThreads`. Read `reviewDecision,latestReviews` and identify approvers by login. Opted-in repositories can count Copilot approvals toward required reviews; they are dismissed on new commits. `APPROVED` does not prove human approval; Copilot uses `copilot-pull-request-reviewer`.

Read `reviews[].body` with `gh pr view --json reviews` as well as inline comments. Copilot's overview can contain “Previously missed” findings without separate inline comments. Rereviews can auto-resolve threads, including “Won't Fix” or “Incorrect” outcomes: resolution alone does not prove a code fix. Refresh thread state after rereviews.

For line-level comments only, use `gh api repos/OWNER/REPO/pulls/NUMBER/comments --paginate`. For thread IDs and resolved state, use GraphQL with `$endCursor: String` and this selection inside `repository { pullRequest(number: $number) { ... } }`:

```graphql
reviewThreads(first: 100, after: $endCursor) {
  nodes {
    id isResolved isOutdated path line originalLine
    comments(first: 20) {
      nodes { author { login } body url createdAt path line originalLine }
      pageInfo { hasNextPage endCursor }
    }
  }
  pageInfo { hasNextPage endCursor }
}
```

The outer cursor does not paginate each thread's comments. Follow each nested `comments.pageInfo` separately using the thread `id` and its comment cursor. For authorized resolution, pass that ID as `threadId` to `resolveReviewThread` or `unresolveReviewThread`, then re-query `isResolved`.

## Missing objects and discussions

If PR/issue view fails, query `repos/OWNER/REPO/pulls/NUMBER` and `repos/OWNER/REPO/issues/NUMBER` with `gh api --include`. They share a number namespace. Distinguish wrong object type, redirects, permissions, and missing/deleted objects.

An admin-archived PR is closed and locked, and returns 404 to non-admins. Check admin access or `is:archived` search before declaring it gone. v2.101.0 exposes neither an archived PR JSON field nor a `--state archived` filter.

`gh discussion view <number-or-url>` (preview) also accepts comment IDs/URLs. Use `--comments` or `--json <fields>` separately; JSON comments do not provide the full paginated thread. For unexposed fields, use GraphQL `repository(owner:, name:) { discussion(number:) { title bodyText url category { name } isAnswered } }`. If unresolved, check `gh repo view OWNER/REPO --json hasDiscussionsEnabled,url`.

## Media attachments

`--attach <path>[#alt text]` on `gh issue create|edit|comment` and `gh pr create|edit|comment` (v2.99+) uploads a user asset. It requires push access and explicit user intent; GHES is unsupported.

- Images: `.png .jpg .jpeg .gif .webp .svg`, up to 10 MB each. Videos: `.mp4 .mov .webm`, client cap 100 MB; Free-plan server cap 10 MB. Maximum 50 attachments; no video alt text.
- With `--body-file`, matching `![alt](./local.png)` references become uploaded URLs and retain alt text; unreferenced files are appended.
- Partial upload failure still creates the issue/PR/comment with successful files and prints its URL, but exits nonzero. Inspect that object before retrying to avoid duplicates.

Example: `gh pr comment <number> --body-file <file> --attach './shot.png#alt text'`.
