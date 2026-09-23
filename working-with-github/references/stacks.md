# Stacked pull requests

`gh stack` is the official `github/gh-stack` extension, separate from core `gh` and in public preview at the September 19, 2026 baseline. Check `gh extension list`; install only with explicit user intent. The repository also provides `skills/gh-stack`.

A stack is an ordered PR chain, each layer targeting the branch below. Inspect with `gh stack view --json` from a checkout; ordinary `gh pr view` still works per layer. History must be linear; cross-fork stacks are unsupported; merge-queue rollout and repository enablement are preview limits.

## Noninteractive commands

| Task | Command |
| --- | --- |
| Inspect | `gh stack view --json` (bare `view` opens a TUI) |
| Check out whole stack | `gh stack checkout <stack-number\|pr-number\|pr-url\|branch>` |
| Initialize/add | `gh stack init <branch>` / `gh stack add <branch>` |
| Submit PRs | `gh stack submit --auto` (add `--open` for non-drafts) |
| Sync | `gh stack sync` (`--prune` deletes merged local branches) |
| Merge selected layer and all below | `gh stack merge <pr-or-stack-number> --yes` |

Bare commands can prompt or open TUIs. `modify` and `switch` are interactive-only. With multiple remotes, pass `--remote <name>` or ensure `remote.pushDefault` is set for `push`, `submit`, `sync`, `rebase`, and `link`.

`checkout` without a target or with a branch name can offer to import a remote stack; `add` can offer initialization. Pass explicit arguments and account for fallback on network errors or ambiguous matches. If another local stack already covers the checkout's branches, it cannot be forced; inspect the conflict before authorized `gh stack unstack --local` and retry. `--local` preserves the GitHub stack.

## Mutation and failure semantics

- `view`, checkout/navigation (`up`, `down`, `top`, `bottom`, `trunk`), `init`, `add`, and `rebase` are local operations. `submit`, `sync`, `push`, `link`, `merge`, and `unstack` without `--local` mutate GitHub and need explicit intent. Apply the core skill's per-instance confirmation rules to destructive/shared-state actions.
- Never use `gh pr merge` on a stacked PR. `gh stack merge` lands every unmerged layer below the selected PR, all-or-nothing. A merge-queue base queues the stack and ignores method flags.
- Lower-layer merges leave upper PRs open, automatically rebased and retargeted. Squash merging with required reviews can require re-approval of remaining layers.
- Diverged `sync` prints both chains and `Sync aborted`, changes nothing, yet exits 0. Stop for a human decision; do not report success. `push` uses force-with-lease but is not atomic across branches.
- Exit codes: 2 = not in a stack; 3 = rebase conflict; 9 = stacked PRs not enabled for the repository.
