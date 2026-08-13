# agent-skills

Skills for [Claude Code](https://claude.com/claude-code).

## Skills

- **[orchestrator](orchestrator/SKILL.md)** — delegate slow, token-heavy work to background workers (Codex CLI processes and Claude subagents) while Claude orchestrates: decompose, spec, dispatch, steer, verify, merge.
- **[frontier-search](frontier-search/SKILL.md)** — frontier-biased adaptive web research loop: tiered sourcing, gap-driven expansion, adversarial fact-check before synthesis.
- **[linear-workflows](linear-workflows/SKILL.md)** — work the Linear MCP surface safely: discover tools at runtime rather than trusting a memorised list, read cheaply, keep `delegate` and `assignee` distinct, and mutate only on request.

## Install

```bash
git clone https://github.com/BigCactusLabs/agent-skills.git
cp -r agent-skills/orchestrator ~/.claude/skills/
```

## License

[MIT](LICENSE)
