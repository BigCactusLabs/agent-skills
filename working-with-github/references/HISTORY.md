# Audit evidence — September 19, 2026

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
