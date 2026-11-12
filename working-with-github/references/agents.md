# GitHub agents

`gh agent-task` runs Copilot cloud tasks; `gh skill` manages skills; both remain preview in the audited CLI. Extension `gh aw` manages Agentic Workflows, generally available on github.com since October 28, 2026. CLI and service maturity differ; check installed help and the [audit](HISTORY.md). API conventions: [CLI/API](cli-and-api.md).

## Copilot tasks

Prefer session IDs/URLs with `gh agent-task view`: PR numbers can need task disambiguation. Use `--log`/`--follow` for logs. REST fallback when CLI coverage is insufficient: `agents/repos/OWNER/REPO/tasks` or `agents/repos/OWNER/REPO/tasks/TASK-ID`; preview token/policy limits apply. Task creation is externally visible and needs explicit intent.

## Skills

Preview third-party contents before install; GitHub does not verify instructions/scripts. Search/preview and update/publish `--dry-run` inspect; install/update/publish/fix mutate and require intent.

Noninteractive installs default to `github-copilot`, project scope. Set `--agent`, `--scope`, or `--dir` for intended placement; `--pin <tag-or-sha>` fixes a version. Verify actual paths, scope, and pins with `gh skill list --json skillName,sourceURL,scope,version,pinned,path` instead of assuming agent directories.

## Agentic Workflows

If `gh aw` is absent, inspect with `gh run` / `gh repo read-file`; do not install unprompted.

Human-authored `.github/workflows/*.md` compiles to sibling `*.lock.yml`, the executed artifact. Inspect both for drift/tampering; runs use standard [Actions](actions.md) diagnosis. Ordinary compile writes locks; `gh aw compile --validate --no-emit` validates without emitting locks but can populate import caches. `gh aw lint` also checks native Actions YAML. Run/trial/deploy and other mutations require intent.

Before trusting mutations, verify effective read permissions, integrity filtering, declared safe outputs, and threat results (`gh aw audit <run-id-or-url>` supplies run evidence). In v0.88.7, `report_incomplete` fails workflows despite agent-process success. Inspect that report before blaming infrastructure.

Before introducing recurring workflows, use `gh aw forecast` when available to estimate AI credits, including threat detection; it is an estimate, not a spending cap. Check installed/upstream versions and migration notes before changing compiled workflows; the pre-1.0 compatibility warnings and token-reporting bugs in the audit describe older builds.
