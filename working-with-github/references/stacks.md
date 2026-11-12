# Stacked PRs

`gh stack` is the `github/gh-stack` extension. Stacked PRs became generally available on github.com on October 6, 2026; do not apply the old preview-enrollment requirement there. Same-repository branches and linear history for merging remain required. Check host availability and installed extension version; the [audit](HISTORY.md) inspected v0.3.0 without installing it.

Inspect from a checkout with `gh stack view --json`; bare `view` opens a TUI. `modify`/`switch` are interactive-only. Use explicit checkout/add targets: omitted/branch targets can offer remote import or initialization. With multiple remotes, select `--remote` or verify `remote.pushDefault` for push/submit/sync/rebase/link.

- Remote writes: submit, sync, push, link, merge, and unstack without `--local`. `submit --auto` creates drafts unless `--open`; `sync --prune` deletes merged local branches.
- Use `gh stack merge`, not `gh pr merge`, for a stacked PR. The selected PR and all unmerged layers below it are in scope. With no target in a noninteractive terminal, the command merges the whole current stack. Confirm the exact layers before executing. Merge-queue bases queue the stack and ignore method flags; queue acceptance is not completion.
- Reviews, required checks, and workflow branch filters use the stack trunk, not each PR's immediate base. Lower-layer merges rebase/retarget open upper PRs. Current server-side rebases retain approvals when the diff is unchanged and generate signed commits; changed diffs still need fresh review evidence.
- Overlapping local stacks cannot be forced. Inspect before authorized `gh stack unstack --local`, which preserves the GitHub stack, then retry.
- A noninteractive sync can stop on divergent stack membership yet exit 0 without pushing branches or updating PRs. Read its output and verify state before reporting success; resolve the divergence with the user.
- In v0.3.0, `push`, `submit`, `sync`, and `link` push branches atomically by default, with explicit force-with-lease checks. `--no-atomic` or `GH_STACK_NO_ATOMIC` opts out. Atomicity covers Git branch updates, not the subsequent PR/stack API writes; inspect remote state before retrying a partial operation.
- `sync`/`rebase` follow a server-retargeted base. If the old base never merged, accepting the change can drop its commits; inspect the ancestry before accepting. `--accept-base-change` suppresses that question and does not supply user authorization.

Exit codes in v0.3.0: 2 = outside stack/not found; 3 = rebase conflict; 6 = ambiguous stack membership; 7 = rebase already in progress; 8 = stack locked. Inspect help/source for version-specific codes.

## Stack-aware CI

For requested CI cost or runtime work, [stack metadata](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/optimizing-ci-for-stacked-pull-requests) can select where expensive jobs run. Guard for `github.event.pull_request.stack != null` before reading its fields:

| Layer | Condition |
| --- | --- |
| Top PR, containing the full stack | `github.event.pull_request.stack.position == github.event.pull_request.stack.size` |
| Lowest unmerged PR, targeting the trunk directly | `github.event.pull_request.stack.base.ref == github.event.pull_request.base.ref` |

`position == 1` identifies the original bottom, not necessarily the lowest unmerged PR after partial merges. Keep normal coverage for non-stack PRs and merge-queue `merge_group` runs. Before applying a filter, verify that selected layers and skipped jobs preserve the trunk's required checks and intended test coverage; a passing top-layer run does not prove every lower layer passes on its own. Measure actual run savings before claiming a reduction.

For custom stack merge automation, see the [async merge API](prs-and-issues.md#async-merge-api), including its downstack scope and queue polling rules.
