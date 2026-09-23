# GitHub agent commands

Three surfaces: `gh agent-task` for Copilot cloud sessions, `gh skill` for installable skills, and `gh aw` for Actions automations. All were preview at the September 19, 2026 baseline. Check help/versions; for API calls, read [CLI and API](cli-and-api.md).

## Copilot tasks

```sh
gh agent-task view <session-id-or-url> -R owner/repo --json completedAt,createdAt,id,name,pullRequestNumber,pullRequestState,pullRequestTitle,pullRequestUrl,repository,state,updatedAt,user
```

Add `--log` or `--follow` only for logs. Prefer a session ID or full URL in scripts: a PR number can require disambiguation among multiple tasks.

Use REST only when CLI coverage is insufficient: list `agents/repos/OWNER/REPO/tasks`, get `agents/repos/OWNER/REPO/tasks/TASK-ID`, or use `/agents/tasks` where needed. Expect preview token/policy limits and states including `queued`, `in_progress`, `completed`, `failed`, `idle`, `waiting_for_user`, `timed_out`, and `cancelled`. `gh agent-task create` and `POST /agents/repos/{owner}/{repo}/tasks` are externally visible mutations requiring explicit intent.

## Agent skills

| Inspection | Command |
| --- | --- |
| Inventory | `gh skill list --json skillName,sourceURL,scope,version,pinned,path` |
| Preview contents | `gh skill preview OWNER/REPO SKILL` |
| Check updates | `gh skill update --dry-run` |
| Validate publishing | `gh skill publish --dry-run` |

Search, preview, and dry-runs are inspection; install/update/publish/fix mutate local or remote state and require explicit intent. Preview third-party contents before install: GitHub does not verify skills, which may contain hidden instructions or scripts.

Noninteractive install defaults to `github-copilot` and project scope. Specify `--agent`, `--scope`, or `--dir` when placement matters; use `--pin <tag-or-sha>` for reproducibility. Multiple hosts share project `.agents/skills`. As of v2.99.0:

| Agent | Project | User | Override |
| --- | --- | --- | --- |
| Copilot | `.agents/skills` | `~/.copilot/skills` | — |
| Codex | `.agents/skills` | `~/.agents/skills` (formerly `~/.codex/skills`) | — |
| Claude Code | `.claude/skills` | `~/.claude/skills` | `CLAUDE_CONFIG_DIR` |
| Pi | `.pi/skills` | `~/.pi/agent/skills` | `PI_CODING_AGENT_DIR` |

Use `gh skill list` to verify actual placement rather than guessing paths.

## Agentic Workflows

`gh aw` comes from `github/gh-aw`, not core `gh`. Check `gh extension list` and `gh aw --help`; do not install unprompted. If absent, inspect with standard `gh run` and `gh repo read-file`.

The human-authored `.github/workflows/*.md` compiles to sibling `*.lock.yml`, the executed artifact. Inspect both for drift or tampering. Runs remain ordinary Actions runs: start with `gh run view <run-id> --log-failed` (see [actions.md](actions.md)).

- Inspection: `gh aw list` / `status` (inventory, enabled state, schedules), `logs <workflow>` (history/metrics), `audit <run-id-or-url>` (safe outputs, threat detection, metrics), `health <workflow>`, `mcp list`, and `models` (v0.87.5+).
- Validation without lock-file writes: `gh aw compile --validate --no-emit` or `gh aw lint`.
- Mutations requiring explicit intent: `init`, `add`, `new`, `compile` (writes locks), `fix --write`, `run`, `trial`, `deploy`, `remove`, `enable`/`disable`, `update`/`upgrade`, and `secrets set`.
- Before trusting an agentic mutation, verify effective read permissions, integrity filtering, declared safe outputs, and threat-detection results.
- In v0.88.7, `report_incomplete` fails the workflow even if the agent process succeeds. Inspect the report before blaming runner infrastructure.
- Compare the installed extension with upstream releases when behavior changes. Minors can break compatibility: built-in Playwright MCP was removed and legacy sandbox flags replaced with runtime profiles. Older builds under-reported token usage as zero; verify the version before trusting that metric.
