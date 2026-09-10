# agent-skills

Skills for [Claude Code](https://claude.com/claude-code).

## Skills

- **[orchestrator](orchestrator/SKILL.md)** — delegate slow, token-heavy work to background workers (Codex CLI processes and Claude subagents) while Claude orchestrates: decompose, spec, dispatch, steer, verify, merge.
- **[frontier-search](frontier-search/SKILL.md)** — frontier-biased adaptive web research loop: tiered sourcing, gap-driven expansion, adversarial fact-check before synthesis.
- **[linear-workflows](linear-workflows/SKILL.md)** — work the Linear MCP surface safely: discover tools at runtime rather than trusting a memorised list, read cheaply, keep `delegate` and `assignee` distinct, and mutate only on request.
- **[working-with-github](working-with-github/SKILL.md)** — drive GitHub through `gh`, `git`, and `gh api`: inspect pasted URLs, PRs, issues, CI runs, releases, discussions, stacked PRs, agent tasks, and agentic workflows before acting; audited against the current gh release with explicit mutation and untrusted-content rules.

## Install

```bash
git clone https://github.com/BigCactusLabs/agent-skills.git
cp -r agent-skills/orchestrator ~/.claude/skills/
cp agent-skills/orchestrator/agents/*.md ~/.claude/agents/   # orchestrator's standing subagent roles
```

## License

[MIT](LICENSE)
