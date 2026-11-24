# GitHub agents

`gh agent-task` (Copilot cloud tasks) and `gh skill` are preview in the audited CLI. Extension `gh aw` (Agentic Workflows) is GA on github.com since October 28, 2026. Versions: [audit](HISTORY.md).

## Copilot tasks

Prefer session IDs/URLs with `gh agent-task view` (PR numbers can be ambiguous); `--log`/`--follow` for logs. REST fallback: `agents/repos/OWNER/REPO/tasks[/TASK-ID]`. Creating a task is externally visible and needs explicit intent.

## Skills

GitHub doesn't verify third-party skill contents: preview before install. Search/preview and update/publish `--dry-run` are read-only; install/update/publish/fix mutate and need intent.

Noninteractive installs default to `github-copilot`, project scope; set `--agent`, `--scope`, or `--dir`, and `--pin <tag-or-sha>` to fix a version. Verify with `gh skill list --json skillName,sourceURL,scope,version,pinned,path`.

## Agentic Workflows

Without `gh aw`, inspect with `gh run` / `gh repo read-file`.

`.github/workflows/*.md` compiles to a sibling `*.lock.yml`, which is what runs; inspect both for drift. Runs use normal [Actions](actions.md) diagnosis. Plain `compile` writes locks; `gh aw compile --validate --no-emit` doesn't (but can fill import caches). `gh aw lint` also checks plain Actions YAML. Run/trial/deploy need intent.

v1.2.3-v1.3.1 tightened defaults (fork admission under `pull_request_target`, protected-file merges, checksum pins for downloads): check release notes when a workflow fails after an upgrade or recompile, and don't loosen them without explicit intent.

Before trusting a run's mutations, check read permissions, integrity filtering, declared safe outputs, and threat results (`gh aw audit <run>`). `report_incomplete` fails a workflow even when the agent process succeeded; read it before blaming infrastructure. Before adding recurring workflows, `gh aw forecast` estimates AI credits (not a cap).
