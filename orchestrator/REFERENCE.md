# Orchestrator — cold-path reference

Material consulted rarely: read the section you need, not the file. Hot-path mechanics (dispatch, supervise, resume, pools) live in `SKILL.md`.

## GPT-5.6 pricing detail

Since the 2026-07-30 cuts: luna −80% to $0.20/$1.20 per Mtok, terra −20% to $2/$12, sol unchanged at $5/$30 — subscription quota credits cut to match. Family GA 2026-07-09. Some model cards showed pre-cut prices as late as 2026-08-02 — trust the CLI source and the canonical pricing table over per-model docs.

## Fast mode

If you ever want fast mode: it needs **both** `-c service_tier=fast` **and** `--enable fast_mode`, is ChatGPT-auth only, and burns credits at 2.5× the standard rate (measured on the prior generation). On the API side, Fast mode replaced Priority Processing on 2026-07-30: sol only, 2× price for up to 2.5× speed, same intelligence — irrelevant for background workers, whose latency the orchestrator absorbs.

## Profiles vs pinned flags

The dispatch template pins flags explicitly so the skill is self-contained regardless of `~/.codex/config.toml`. Profiles — `-p <name>` layering `~/.codex/<name>.config.toml` — can replace the pins, but codex hard-errors if legacy `[profiles.*]` tables remain in `config.toml`; explicit flags are more portable.

## Reaching gpt-5.6 from inside Workflow scripts

Workflow scripts' `model:`/`agentType:` params only take Claude values. Reach gpt-5.6 by wrapping: spawn a cheap Claude agent (`model: 'sonnet'`, `effort: 'low'`) instructed to compose the self-contained spec, run `codex exec` per `SKILL.md`, verify, and return the last-message file's content verbatim.

## codex mcp-server

`codex mcp-server` exposes `codex`/`codex-reply` tools over MCP — an alternative wiring, but background `codex exec` keeps the kill/steer control this skill relies on.

## Native Codex multi-agent (v2 stable as of 0.145.0)

Codex can spawn its own sub-agent threads; settings are unified under `[agents]` in config.toml (verified against 0.145.0 source: `enabled` default true, with an enabled `features.multi_agent_v2` taking precedence; `max_concurrent_threads_per_session`, alias `max_threads`; `default_subagent_model` / `default_subagent_reasoning_effort` for spawns that don't pick their own; per-role `[agents.<role>]` tables; `max_depth` is V1-only, ignored by V2). This skill deliberately doesn't orchestrate through it — you are the orchestrator, and separate dispatches keep per-worker kill/steer control. That's not just preference: V2 subagents live behind parent-owned mailboxes (path addresses like `/root/agent_a`, structured envelopes), and the app-server *rejects* external input to a spawned child (openai/codex#27173) — an outside orchestrator physically cannot steer inside a worker's fan-out. A worker may still fan out internally on its own; that's fine, your verification is on the final diff either way. (0.146.0 adjacent: agent-plugin manifests + marketplaces landed, including a Claude Code-format marketplace — cross-harness skill reuse exists, but changes nothing about dispatch mechanics.) The `spawn_agents_on_csv` batch primitive was **removed** in 0.145.0 (#34413; `job_max_runtime_seconds` survives only as a config no-op) — official docs still describe it, ignore them.

## Agent teams mechanics

(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`): peer Claude sessions with a shared dependency-tracked task list, inter-agent messaging, plan-approval gates, and quality hooks (`TeammateIdle`, `TaskCreated`, `TaskCompleted` — exit 2 sends feedback and keeps the teammate working). Enable via the env var in settings (`env` block; takes effect for sessions started afterward). Mechanics (verified against docs + changelog 2026-08-02): since v2.1.178 every session is one implicit team — spawn teammates via the Agent tool's `name` param and message by name (`team_name` accepted but ignored; `TeamCreate`/`TeamDelete` removed — third-party guides describing them are stale). Subagent definitions double as teammate roles (`tools`/`model` honored; `skills`/`mcpServers` frontmatter ignored). Teammates don't inherit the lead's `/model` (set "Default teammate model" in `/config`) but do inherit its effort level. Display default is `in-process` since v2.1.179 (**not** `auto`); split panes require tmux or iTerm2+`it2` and don't work in VS Code's terminal/Windows Terminal/Ghostty. Cost control: official estimate ~7× a standard session with plan-mode teammates — use Sonnet teammates, 3-5 of them, ~5-6 tasks each, shut them down when done. Known limits — no `/resume`/`/rewind` of in-process teammates (lead may message dead teammates after resume), no nested teams, no background subagents from an in-process teammate, task-status can lag (nudge or update manually), one fixed lead/team per session, and no automatic worktree isolation — partition by file ownership; teams are debating peers, not a locking system (task-claim locks don't guard file edits).

## Watch items (not adopted)

- **`openai/codex-plugin-cc`** (official OpenAI plugin, v1.0.6 2026-07-08, ~29k stars) runs Codex inside Claude Code — `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`, `/codex:transfer`, background jobs, optional Stop-hook review gate; wraps the local codex binary and its auth (not MCP). Not adopted: background `codex exec` keeps the kill/steer control this skill relies on. Evaluate on next audit; OpenAI warns its auto review loop can drain usage limits.
- **Remote lanes (probed 2026-07-17; neither usable-verified — no engine-table row):** `codex cloud` exists (experimental: `exec`/`status`/`list`/`apply`/`diff` — submit a cloud task, poll, apply the diff locally; surface unchanged on 0.145.0); help-text verified only — evaluate end-to-end before relying on it. The Agent tool's `isolation: "remote"` is gated and **falls back to local silently** (identity probe: same hostname/user/cwd — the fallback looks exactly like success), so probe before trusting it. Without docker, container-per-worker isolation is out; per-worker ports/temp/DB names (Worker pools in `SKILL.md`) remain the tool.
