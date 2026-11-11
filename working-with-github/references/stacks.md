# Stacked PRs

`gh stack` is the `github/gh-stack` extension; [audited](HISTORY.md) preview limits include linear history, no cross-fork stacks, and repository/merge-queue enablement.

Inspect from a checkout with `gh stack view --json`; bare `view` opens a TUI. `modify`/`switch` are interactive-only. Use explicit checkout/add targets: omitted/branch targets can offer remote import or initialization. With multiple remotes, select `--remote` or verify `remote.pushDefault` for push/submit/sync/rebase/link.

- Remote writes: submit, sync, push, link, merge, and unstack without `--local`. `submit --auto` creates drafts unless `--open`; `sync --prune` deletes merged local branches.
- Never use `gh pr merge` on a stacked PR. `gh stack merge` lands the selected PR and all unmerged layers below, all-or-nothing. Merge-queue bases queue the stack and ignore method flags.
- Lower-layer merges rebase/retarget open upper PRs; partial squash merges can require new approvals.
- Overlapping local stacks cannot be forced. Inspect before authorized `gh stack unstack --local`, which preserves the GitHub stack, then retry.
- Diverged sync prints `Sync aborted`, changes nothing, yet exits 0: stop for a human decision. Push uses force-with-lease but is not atomic across branches.

Exit codes: 2 = outside stack; 3 = rebase conflict; 9 = repository lacks stacked-PR enablement.
