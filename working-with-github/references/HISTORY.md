# Audit evidence

Dated evidence for rechecking claims, not a current capability guarantee. Operational instructions live in the task references.

## September 19, 2026

Installed/upstream CLI: v2.101.0 (September 15). Latest extensions: gh-aw v0.88.7 and gh-stack v0.1.1; neither was installed locally. Extension behavior was checked in releases/source, not executed.

| Finding | Primary evidence |
| --- | --- |
| CLI release; Linux APT/RPM signing-key migration (do not disable signature checks; Homebrew unaffected) | [v2.101.0](https://github.com/cli/cli/releases/tag/v2.101.0) |
| Experimental `api_host` routing is not a security boundary | [v2.100.0](https://github.com/cli/cli/releases/tag/v2.100.0) |
| REST versions `2026-03-10`, `2022-11-28`; recorded security floor v2.98.0, not proof of no vulnerabilities | [Versions](https://api.github.com/versions), [advisories](https://github.com/cli/cli/security/advisories) |
| Queued rerun can retain an older passing check; source-verified, not reproduced end to end; proposed fix closed unmerged | [#14371](https://github.com/cli/cli/issues/14371), [v2.101.0 sorting](https://github.com/cli/cli/blob/v2.101.0/pkg/cmd/pr/checks/aggregate.go), [#14478](https://github.com/cli/cli/pull/14478) |
| `cache-mode` write overrides can exceed low-trust defaults | [September 10 announcement](https://github.blog/changelog/2026-09-10-control-github-actions-cache-access-with-cache-mode/) |
| Execution protections GA; default `pull_request_target` block initially evaluate-only, enforcement announced for November 2 | [September 17 announcement](https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available) |
| Copilot overview-only findings and automatic thread resolution | [September 18 announcement](https://github.blog/changelog/2026-09-18-copilot-code-review-an-improved-review-experience) |
| `report_incomplete` fails agentic workflows even after agent-process success | [gh-aw v0.88.7](https://github.com/github/gh-aw/releases/tag/v0.88.7), [change definition](https://github.com/github/gh-aw/blob/v0.88.7/.changeset/fix-report-incomplete-conclusion.md) |
| Stack preview baseline | [gh-stack v0.1.1](https://github.com/github/gh-stack/releases/tag/v0.1.1) |

Local help confirmed PR JSON fields (no `reviewThreads`), pending-check exit 8, remote reads, and `api_host`. Live GraphQL introspection confirmed thread IDs, comment connections, and `ResolveReviewThreadInput.threadId`. The query returned 17 threads on cli/cli#14104; none required nested pagination, so that branch was not exercised. Skill validation, whitespace, and local links passed. No merge, rerun, upload, install, or policy mutation was exercised.

## Earlier security and compatibility record

September 2 snapshot; retained for targeted re-verification. See the [CLI advisory ledger](https://github.com/cli/cli/security/advisories) and versioned releases for details.

| Fixed in | Security issue |
| --- | --- |
| v2.92.0 | Terminal escape injection in Actions logs |
| v2.93.0 | Authorization-header leak to TUF mirrors during attestation/release verification |
| v2.96.0 | Command execution from malicious Codespace Jupyter URLs |
| v2.97.0 | Escape injection in gist/API/PR diff; URL-path request redirection; PAT leakage in auth status; attestation certificate regex bypass |
| v2.98.0 | Codespace forwarded ports bound to all interfaces instead of loopback (GHSA-vfhh-p7hm-pxfh) |

Useful compatibility points: discussions v2.94; remote reads v2.95; public unauthenticated release downloads v2.96; PR worktrees and semantic/hybrid issue search v2.98; attachments, issue worktrees, exclusive `--comments`/`--json`, revised skill placement, and linked-worktree protections v2.99. Details are in the task references; verify current help before use.

Agentic Workflows v0.88 introduced runtime profiles and removed built-in Playwright MCP; v0.81.6 fixed zero token-usage reporting. Stack preview limits included linear history, no cross-fork stacks, and possible review invalidation after partial squash merges.
