# agent-skills

Skills for [Claude Code](https://claude.com/claude-code).

## Skills

- **[orchestrator](orchestrator/SKILL.md)** — delegate slow, token-heavy work to background workers (Codex CLI processes and Claude subagents) while Claude orchestrates: decompose, spec, dispatch, steer, verify, merge.

## Install

```bash
git clone https://github.com/BigCactusLabs/agent-skills.git
cp -r agent-skills/orchestrator ~/.claude/skills/
```

## License

[MIT](LICENSE)
