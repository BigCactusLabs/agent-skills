# GitHub agents

`gh agent-task` runs Copilot cloud tasks; `gh skill` manages skills; extension `gh aw` manages Actions automations. All were preview at the [audit](HISTORY.md). API conventions: [CLI/API](cli-and-api.md).

## Copilot tasks

Prefer session IDs/URLs with `gh agent-task view`: PR numbers can need task disambiguation. Use `--log`/`--follow` for logs. REST fallback when CLI coverage is insufficient: `agents/repos/OWNER/REPO/tasks` or `agents/repos/OWNER/REPO/tasks/TASK-ID`; preview token/policy limits apply. Task creation is externally visible and needs explicit intent.

## Skills

Preview third-party contents before install; GitHub does not verify instructions/scripts. Search/preview and update/publish `--dry-run` inspect; install/update/publish/fix mutate and require intent.

Noninteractive installs default to `github-copilot`, project scope. Set `--agent`, `--scope`, or `--dir` for intended placement; `--pin <tag-or-sha>` fixes a version. Verify actual paths, scope, and pins with `gh skill list --json skillName,sourceURL,scope,version,pinned,path` instead of assuming agent directories.

## Agentic Workflows

If `gh aw` is absent, inspect with `gh run` / `gh repo read-file`; do not install unprompted.

Human-authored `.github/workflows/*.md` compiles to sibling `*.lock.yml`, the executed artifact. Inspect both for drift/tampering; runs use standard [Actions](actions.md) diagnosis. Ordinary compile writes locks; `gh aw compile --validate --no-emit` or `gh aw lint` validates without lock writes. Run/trial/deploy and other mutations require intent.

Before trusting mutations, verify effective read permissions, integrity filtering, declared safe outputs, and threat results (`gh aw audit <run-id-or-url>` supplies run evidence). In v0.88.7, `report_incomplete` fails workflows despite agent-process success. Inspect that report before blaming infrastructure.

Check installed/upstream versions for behavior changes: minors can break compatibility, and older builds incorrectly reported zero token usage. Migration evidence is in the audit.
