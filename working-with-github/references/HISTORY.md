# Audit evidence

## November 12, 2026

Installed CLI: v2.103.3. Latest upstream release: v2.104.0, published during this audit date. Latest extensions checked: gh-stack v0.3.0 and gh-aw v1.2.2; neither is installed. The CLI, stack, and Agentic Workflows repositories were active and not archived. Versioned source/help and live owner documentation support this update; extension behavior was not executed.

| Finding | Primary evidence |
| --- | --- |
| v2.102.0 fixes symlink destination writes, skill-search argument injection, and two attestation policy-matching flaws; replaces the earlier security floor for these operations | [Release and four advisories](https://github.com/cli/cli/releases/tag/v2.102.0) |
| v2.103.0 adds opt-in expiring credentials and private-preview issue artifacts; environment tokens do not refresh | [Release](https://github.com/cli/cli/releases/tag/v2.103.0), [versioned CLI guidance](https://github.com/cli/cli/blob/v2.103.3/skills/gh/SKILL.md) |
| v2.103.2 defers attachment token eligibility to the server, including supported GitHub App tokens | [Release](https://github.com/cli/cli/releases/tag/v2.103.2) |
| v2.104.0 requires explicit acceptance of cascading private-fork deletion, including with `--yes` | [Release](https://github.com/cli/cli/releases/tag/v2.104.0) |
| `--match-head-commit` guards the verified PR head; merge queues can leave a successful command queued rather than merged | [Merge manual](https://cli.github.com/manual/gh_pr_merge) |
| Queued-rerun stale-pass warning remains relevant: issue open, old proposed fix closed unmerged, latest release still sorts by `StartedAt` alone | [Issue](https://github.com/cli/cli/issues/14371), [v2.104.0 source](https://github.com/cli/cli/blob/v2.104.0/pkg/cmd/pr/checks/aggregate.go), [closed fix](https://github.com/cli/cli/pull/14478) |
| REST versions remain `2026-03-10` and `2022-11-28`; unversioned requests still default to the latter, whose support ends March 10, 2028 | [Version policy](https://docs.github.com/en/rest/about-the-rest-api/api-versions) |
| Public-repo `pull_request_target` default block moved to December 2; November 9/16 brownouts can create failed runs without execution | [November 2 announcement](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2/) |
| Retention now covers Actions and third-party checks/statuses; increasing retention does not restore evicted data | [October 1 announcement](https://github.blog/changelog/2026-10-01-actions-retention-now-covers-checks-runs-and-statuses/) |
| Actions dependency lockfiles are GA, separate from compiled Agentic Workflow YAML; reusable workflow calls are outside dependency-lock coverage | [GA announcement](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/), [coverage](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles), [generation/update behavior](https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies) |
| Stacked PRs are GA on github.com; rules/CI use the trunk; unchanged server-rebased diffs retain approvals | [GA announcement](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/), [current stack requirements](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests) |
| gh-stack v0.3.0 pushes atomically by default, excluding PR/stack API transactions; retargeted bases can require acceptance before dropping unmerged commits | [Release](https://github.com/github/gh-stack/releases/tag/v0.3.0), [versioned command reference](https://github.com/github/gh-stack/blob/v0.3.0/README.md) |
| Divergent noninteractive stack sync can still exit successfully without completing | [v0.3.0 sync source](https://github.com/github/gh-stack/blob/v0.3.0/cmd/sync.go) |
| Agentic Workflows are GA; forecast includes threat detection; `compile --no-emit` can still populate import caches | [GA announcement](https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/), [v1.2.2 CLI reference](https://github.com/github/gh-aw/blob/v1.2.2/docs/src/content/docs/setup/cli.md), [release](https://github.com/github/gh-aw/releases/tag/v1.2.2) |
| Async merge API is GA and recommended for custom merge automation; pending requests have UUIDs, `enqueued` is terminal without proving merge, and results expire after 24 hours | [GA announcement](https://github.blog/changelog/2026-10-01-github-async-merge-api-generally-available/), [API contract](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request-asynchronously) |
| Stack metadata distinguishes the top and lowest unmerged PR for CI job selection; original position 1 is not always the lowest unmerged layer | [CI guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/optimizing-ci-for-stacked-pull-requests) |
| gh-actions-lock v0.4.1 separates offline coverage from online provenance verification; container images and reusable workflow calls are outside lock coverage | [Versioned reference](https://github.com/github/gh-actions-lock/blob/v0.4.1/README.md) |
| zizmor v1.32.0, released November 2, adds experimental lockfile support; optional trial recommended before wider adoption | [Release](https://github.com/zizmorcore/zizmor/releases/tag/v1.32.0), [limitations](https://docs.zizmor.sh/usage/#workflow-lockfiles), [maintainer tracking](https://github.com/zizmorcore/zizmor/issues/2477) |

Counter-checks: the v0.3.0 stack README says queued stacks may land in separate groups, while the current server reference and GA announcement describe keeping stacks together. Use current server documentation for that behavior and verify the final PR states; this audit did not exercise a merge queue. The queued-check warning was retained after reading the current implementation, not inferred solely from issue comments. Search indexing initially showed v2.103.3 as latest; the live releases API supplied v2.104.0.

Verification: installed help confirmed credential inspection/refresh behavior, API method switching and pagination, merge head matching, preview issue artifacts, and that `gh pr create --dry-run` can push. Versioned CLI guidance confirmed attachment routing. Live read-only API calls checked releases, lifecycle, advisories, supported REST versions, and explicit GET query parameters. Skill validation and local reference/Markdown checks passed. No merge, rerun, deletion, upload, extension installation, credential-setting change, or policy mutation was tested.

Follow-up verification: read the async merge contract, stack CI conditions, gh-actions-lock v0.4.1 reference, and zizmor v1.32.0 release/limitations. Both lockfile-tool repositories were active and not archived. No async merge, CI-filter rollout, lockfile extension, or zizmor execution was tested; no CI savings were measured.

Tier coverage: T1 owner docs/releases and T2 repository/source/advisory records; the follow-up also checked T4/T5 maintainer discussion for experimental zizmor support. T3 research was not needed for command maintenance; repeated same-owner evidence is one origin, not independent corroboration.

*Adapted: Kept research focused on changes since the prior audit, resolved stale dates against newer owner announcements, and checked installed capabilities separately from upstream releases.*

## September 19, 2026

Dated evidence, not current guarantees. CLI installed/upstream: v2.101.0; extensions: gh-aw v0.88.7, gh-stack v0.1.1, neither installed. Extension behavior was source-checked, not executed. Recheck current releases/help for capability or migration decisions.

| Finding | Primary evidence |
| --- | --- |
| CLI baseline; Linux APT/RPM signing-key migration: retain signature checks (Homebrew unaffected) | [v2.101.0](https://github.com/cli/cli/releases/tag/v2.101.0) |
| `api_host` routing is not a security boundary | [v2.100.0](https://github.com/cli/cli/releases/tag/v2.100.0) |
| REST versions `2026-03-10`, `2022-11-28`; unversioned default was latter | [Versions](https://api.github.com/versions) |
| Recorded security fixes require v2.98.0+; this is not a vulnerability-free guarantee | [Advisory ledger](https://github.com/cli/cli/security/advisories) |
| Queued rerun can retain old pass; source-verified, not reproduced end to end; proposed fix closed unmerged | [Issue](https://github.com/cli/cli/issues/14371), [sorting source](https://github.com/cli/cli/blob/v2.101.0/pkg/cmd/pr/checks/aggregate.go), [closed fix](https://github.com/cli/cli/pull/14478) |
| Cache writes can override low-trust defaults | [Announcement](https://github.blog/changelog/2026-09-10-control-github-actions-cache-access-with-cache-mode/) |
| Execution protections: initial evaluate mode; enforcement announced for November 2 | [Announcement](https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available) |
| Copilot overview-only findings and automatic thread resolution | [Announcement](https://github.blog/changelog/2026-09-18-copilot-code-review-an-improved-review-experience) |
| `report_incomplete` fails workflows despite agent-process success | [gh-aw v0.88.7](https://github.com/github/gh-aw/releases/tag/v0.88.7), [change](https://github.com/github/gh-aw/blob/v0.88.7/.changeset/fix-report-incomplete-conclusion.md) |
| Stack preview limits | [gh-stack v0.1.1](https://github.com/github/gh-stack/releases/tag/v0.1.1) |

Verification: local help confirmed PR JSON lacks `reviewThreads`, pending-check exit 8, remote reads, and `api_host`. Live GraphQL confirmed thread IDs/comment connections and `ResolveReviewThreadInput.threadId`; 17 threads on cli/cli#14104 did not exercise nested pagination. No merge, rerun, upload, install, or policy mutation was tested.

Earlier gh-aw migration points: v0.88 replaced legacy sandbox flags with runtime profiles and removed built-in Playwright MCP; v0.81.6 fixed zero token-usage reporting. Consult versioned releases when diagnosing those behaviors.
