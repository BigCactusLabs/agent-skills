# Actions and CI diagnosis

Baseline: September 19, 2026; sources in [HISTORY.md](HISTORY.md). For API calls, read [CLI and API](cli-and-api.md) for headers and pagination.

## Inspect the exact run

Extract `owner/repo`, `run-id`, and any attempt/job ID from the URL. Start with:

```sh
gh run view <run-id> -R owner/repo --json attempt,conclusion,displayTitle,event,headBranch,headSha,jobs,name,status,url,workflowName
gh run view <run-id> -R owner/repo --log-failed
```

Add `--attempt <attempt>` to both when known. For a specific job, use `gh run view -R owner/repo --job <job-id> --log-failed`. If context remains unclear, query `repos/OWNER/REPO/actions/runs/<run-id>/jobs` with `gh api`.

| Need | Command |
| --- | --- |
| Find runs | `gh run list -R owner/repo --branch <branch> --commit <sha> --json databaseId,headBranch,headSha,status,conclusion,url` |
| Watch active run | `gh run watch <run-id> -R owner/repo --compact --exit-status` |
| Poll if a fine-grained PAT lacks watch's `checks:read` | `gh run view <run-id> -R owner/repo --json status,conclusion,url` |
| Download artifacts | `gh run download <run-id> -R owner/repo -D <dir>` |
| Rerun failed jobs (mutation) | `gh run rerun <run-id> -R owner/repo --failed` |
| Dispatch (mutation) | `gh workflow run <workflow-id-or-file> -R owner/repo --ref <ref>` |

For a single-job rerun, obtain `databaseId` from `gh run view <run-id> --json jobs`, then pass it to `gh run rerun <run-id> --job <databaseId>`. Do not substitute the browser job URL number.

## Checks and incomplete logs

After opening/updating a PR, run `gh pr checks <number-or-url> --watch`; add `--required` for merge-blocking checks only. Without watch, exit 8 means pending.

In v2.101.0, duplicate-check sorting can keep an old pass while an unstarted rerun is queued ([#14371](https://github.com/cli/cli/issues/14371)). After rerunning, verify the specific run/attempt with `gh run view <run-id> --json attempt,headSha,status,conclusion,url`. For external checks, inspect `repos/OWNER/REPO/commits/SHA/check-runs --paginate` via `gh api` for the current head. Exit 0 alone is insufficient in this case.

`gh` can fail to associate zipped logs with jobs, show `UNKNOWN STEP`, or fail when more than 25 job logs are missing. Try the specific job log, then use `gh api -i repos/OWNER/REPO/actions/runs/<run-id>/logs` and follow the `Location` redirect for the archive. Background steps (`background: true`, `wait`/`wait-all`, `cancel`, `parallel`) keep separate logs: match by step name, not position.

## Permissions, cache, and execution policy

Before diagnosing permission, cache, or checkout failures, establish the trigger, actor trust, head/base repositories, checked-out ref, token permissions, execution policy, and effective `cache-mode`. A denied cache save or protected fork-head checkout under `pull_request_target` can be intentional. Do not recommend `allow-unsafe-pr-checkout` or broader token permissions without explicit user intent and a concrete security review.

- `cache-mode`: `read`, `write`, `write-only`, or `none`. Job settings override workflow settings; reusable workflows cannot exceed caller access. Without an override, untrusted default-branch scopes are read-only. Explicit `write`/`write-only` can override low-trust defaults and emit a warning. Do not grant writes just to silence it; check the effective mode for denied saves or restores.
- Execution protections became GA September 17, 2026, including workflow-file targeting, Insights, and REST management. A rejected dispatch may be actor/event policy, not a bad ref. A default `pull_request_target` block starts in evaluate mode for affected public repositories without an applicable event policy; announced enforcement is November 2. Inspect policy/Insights before changing workflows.
- From October 1, 2026, checks, workflow runs, and commit statuses follow Actions retention (default 90 days; public repositories capped at 90), non-retroactively, replacing the former 400+ days. For older commits, empty run/check results may mean expired history, not that CI never ran. Check retention before concluding.

For Markdown agentic workflows and `.lock.yml` diagnosis, read [agents.md](agents.md).
