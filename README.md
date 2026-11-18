# agent-skills

Skills for [Claude Code](https://claude.com/claude-code) and Codex.

## Skills

- **[codex-orchestrator](codex-orchestrator/SKILL.md)** — coordinate bounded worker tasks under GPT-6 Astra in Codex, with native-agent, CLI-worker, review, and opt-in persisted-bridge guidance.
- **[orchestrator](orchestrator/SKILL.md)** — delegate slow, token-heavy work to background workers (Codex CLI processes and Claude subagents) while Claude orchestrates: decompose, spec, dispatch, steer, verify, merge.
- **[cm-orchestrator](cm-orchestrator/SKILL.md)** — the code-mode edition of orchestrator, for a Claude Code lead whose tools are `REPL` and `Poll`: the same policy, with the launch, wait, stop, and steer mechanics written as scripts. It uses orchestrator's references and scripts, so install both.
- **[frontier-search](frontier-search/SKILL.md)** — frontier-biased adaptive web research loop: tiered sourcing, gap-driven expansion, adversarial fact-check of the draft before the answer.
- **[task-context-enrichment](task-context-enrichment/SKILL.md)** — add verified implementation context (current state, where to start, constraints, validation, first step) to existing backlog tasks so a later implementer can start work; does not do the tasks or change their status.
- **[working-with-excel-workbooks](working-with-excel-workbooks/SKILL.md)** — read, create, edit, recalculate, repair, and verify Excel files: choose a backend by job and required fidelity, keep formulas and workbook objects intact in existing templates, and check cached formula values before trusting them.
- **[working-with-github](working-with-github/SKILL.md)** — drive GitHub through `gh`, `git`, and `gh api`: inspect pasted URLs, PRs, issues, CI runs, releases, discussions, stacked PRs, agent tasks, and agentic workflows before acting; audited against the current gh release with explicit mutation and untrusted-content rules.

## Install

```bash
git clone https://github.com/BigCactusLabs/agent-skills.git
cp -r agent-skills/codex-orchestrator ~/.codex/skills/
cp -r agent-skills/orchestrator ~/.claude/skills/
cp -r agent-skills/cm-orchestrator ~/.claude/skills/   # code-mode edition; needs orchestrator beside it
cp agent-skills/orchestrator/agents/*.md ~/.claude/agents/   # orchestrator's standing subagent roles
```

## License

[MIT](LICENSE)
