# Stacked PRs

`gh stack` is the `github/gh-stack` extension. Stacked PRs are GA on github.com (October 6, 2026; no enrollment needed). Branches must be in the same repo with linear history. Check host availability and installed version ([audit](HISTORY.md): v0.3.0).

Inspect from a checkout with `gh stack view --json` (bare `view` opens a TUI). `modify`/`switch` are interactive-only. Give explicit checkout/add targets; omitted targets can offer remote import or init. With multiple remotes, pass `--remote` or verify `remote.pushDefault`.

- Remote writes: submit, sync, push, link, merge, and unstack without `--local`. `submit --auto` creates drafts unless `--open`; `sync --prune` deletes merged local branches.
- Merge stacked PRs with `gh stack merge`, never `gh pr merge`. Scope is the selected PR plus every unmerged layer below; with no target in a noninteractive terminal it merges the whole stack. Confirm the exact layers. Merge-queue bases queue the stack and ignore method flags; queued is not merged.
- Reviews, required checks, and branch filters use the stack trunk, not each PR's base. Lower merges rebase/retarget upper PRs; server rebases keep approvals only when the diff is unchanged.
- Overlapping local stacks can't be forced: inspect, then (authorized) `gh stack unstack --local`, which keeps the GitHub stack, and retry.
- Noninteractive `sync` can stop on divergent membership yet exit 0 without pushing. Read its output and verify state; resolve with the user.
- `push`/`submit`/`sync`/`link` push atomically (opt out: `--no-atomic` / `GH_STACK_NO_ATOMIC`). Atomicity excludes the PR/stack API writes after; inspect remote state before retrying.
- `sync`/`rebase` follow a server-retargeted base; if the old base never merged, accepting can drop its commits. Check ancestry first. `--accept-base-change` is not user authorization.

Exit codes (v0.3.0): 2 not in stack/not found; 3 rebase conflict; 6 ambiguous membership; 7 rebase in progress; 8 stack locked.
