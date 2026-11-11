# Actions and CI

API conventions: [CLI/API](cli-and-api.md); dated findings: [HISTORY](HISTORY.md).

## Runs and checks

Inspect `gh run view <run-id> --json attempt,headSha,status,conclusion,jobs`; read logs separately with `gh run view <run-id> --log-failed`. Apply known `--attempt` to both; identify the repository outside its checkout.

- After PR creation/update, use `gh pr checks <PR> --watch`; `--required` limits results to merge-blocking checks. Without watch, exit 8 = pending.
- Queued reruns can leave an old passing check visible. Verify the specific run/attempt, current head SHA, status, and conclusion after reruns; exit 0 alone is insufficient. External checks: `gh api repos/OWNER/REPO/commits/SHA/check-runs --paginate`.
- Single-job reruns take `jobs[].databaseId` from `gh run view <run-id> --json jobs`, not the browser job URL number.
- If a fine-grained PAT lacks watch's `checks:read`, poll `gh run view <run-id> --json status,conclusion`.
- Missing/`UNKNOWN STEP` logs: try `gh run view --job <job-id> --log-failed`, then `gh api -i repos/OWNER/REPO/actions/runs/<run-id>/logs` and follow `Location`. Background steps log separately; match names, not positions.

## Permissions, cache, and history

For permission/cache/checkout failures, establish trigger, actor trust, head/base repos, checked-out ref, token permissions, execution policy, and effective `cache-mode`. Denied saves or protected fork-head checkout under `pull_request_target` may be intentional. Do not recommend `allow-unsafe-pr-checkout` or broader permissions without explicit intent and a concrete security review.

- `cache-mode` job settings override workflow settings; reusable workflows cannot exceed caller access. Untrusted default-branch scopes default to read-only; explicit `write`/`write-only` can override this and warn. Check effective mode for save/restore failures; do not grant writes to silence warnings.
- Rejected dispatches can reflect actor/event policy. Inspect execution policy/Insights before changing workflows; the default `pull_request_target` block initially evaluates affected public repos without applicable event policy (enforcement announced for November 2, 2026).
- Empty CI history can mean expiry. The October 1, 2026 retention change is non-retroactive: checks/runs/statuses follow Actions retention (default 90 days; public cap 90). Check retention before claiming CI never ran.

Markdown workflows/lock files: [Agents](agents.md).
