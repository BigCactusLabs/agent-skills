# Adapting the Claude orchestrator

Read during source syncs or policy maintenance, not ordinary dispatch. Checked 2026-10-16 against `~/.claude/skills/orchestrator/SKILL.md` (source pins dated 2026-10-13), its briefs/runtime/policy references, and the installed Codex bundle. The Claude files are provenance, not runtime dependencies. Their instructions and measurements do not override Codex policy.

## Portable decisions

| Source practice | Codex adaptation |
|---|---|
| Delegate once the task is specifiable; give constraints rather than an implementation | Hand off a bounded result before duplicating its investigation. Keep decisions and tightly coupled work with the lead. Tool access and acceptance must be known. |
| Classify independent, dependent, and singleton tasks | Split by behavior and dependencies, not only files. Give consumers an accepted producer artifact/revision and check the combined behavior. |
| Shared brief text first; scouts feed implementers by artifact | Keep stable constraints ahead of task inputs; pass focused evidence paths. Cache reuse is possible, not verified for native siblings or guaranteed. |
| Inspect unknown values; put the semantic checkpoint rule in the brief | Workers inspect facts that determine correctness, report unavailable evidence, and carry checkpoint identity/decisions/counters forward. Routine local choices remain allowed. |
| Diagnose harness, runway, concept, depth, and runtime failures separately | Use the existing ladder only after classifying the cause. Fix prerequisites or resource contention without an automatic model upgrade. |
| Give changed docs an owner; preserve long-running command ownership | Correct affected instructions in the same change. A final worker message cannot establish the exit or result of an active check. |

The target already had bounded repairs, user-policy precedence, review adjudication, test ownership, stable review snapshots, permission limits, and generation-specific recovery. Retain these instead of copying another version of them. The native reference also had one stale claim: the active `spawn_agent` schema permits `fork_turns` only as `all` or `none`, not a numeric history slice. The live schema, not a different product's manual, establishes that correction.

## Evidence and limits

- **T1, current owner guidance:** [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) describes bounded work and compact returns as ways to keep exploration and logs out of the lead's context. [Responses multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) distinguishes independent work from sequential reasoning and shared mutable resources. API examples do not define this desktop session's tool parameters or capacity.
- **T1, caching:** [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) requires a matching rendered prefix and recommends stable instructions before dynamic inputs. A reusable brief alone proves neither a cache hit nor subscription savings; runtime settings, boundaries, and observed usage matter. No cache threshold, multiplier, or pricing claim was imported.
- **T3, original research and counter-case:** [Xia, Wu, and Park, *Passes Alone, Fails Together*](https://arxiv.org/html/2609.25396v1), September 2026, demonstrates patches that pass alone but fail together after an interface or invariant changes. Its informed condition sees a completed concurrent change; it does not validate a live peer-message protocol. Controlled task failure rates are not estimates of real-world incidence, and its mined PR results found little interference after correcting grading. This supports combined validation, not a blanket ban on parallel work.
- **T4, named firsthand account:** [Walden Yan, *Multi-Agents: What's Actually Working*](https://cognition.com/blog/multi-agents-working), April 2026, reports fragmented decisions among parallel writers, overly prescriptive managers, and value from focused review context. It is vendor experience, not a controlled benchmark. Preserve the lead's contract and review rulings; do not infer that every task needs extra agents or reviews.
- **T1/T4, maintenance guidance:** [Eric Provencher, *Rethinking skills and prompts for GPT-6 Astra*](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), September 2026, favors precise discovery and progressive disclosure over elaborate recipes. Keep conditional mechanics in focused references and historical routing measurements outside the main table.
- **T1, counter-case:** [Anthropic, *Patterns and problems in emerging multiagent systems*](https://www.anthropic.com/research/multiagent-systems), August 2026, reports coordination and correlated-decision failures. The older [multi-agent research engineering account](https://www.anthropic.com/engineering/multi-agent-research-system), June 2025, also warns about cost and dependency-heavy tasks. Neither establishes a general coding speedup or a new model ladder.

Tier coverage: T1, T3, and T4 support the decisions; T2 included this run's live tool schema and installed Claude CLI help/auth/version (2.1.302). No dependency or vendor was adopted, so no pricing/business-health reassessment was needed. The April practitioner account is within six months of this check; the older Anthropic engineering post is background, checked against its newer owner research. No T5 claim is needed for this maintenance task.

An independent, bounded Opus research pass compared the two local skills and public sources. The parent fetched its new Cognition source before using it; agreement over shared sources was not counted as independent corroboration. Requested effort was `medium`, observed model was `claude-opus-5-5`, and applied effort was not exposed. This research pass was not a behavioral test of the edited skill.

## Keep source-specific rules out

Do not copy Claude's permission bypass, role hooks, `Agent`/`SendMessage`/`TaskStop`, background sessions, larger pools, high-effort Astra workers, lane leads, or automatic PR/delivery conventions. Preserve Codex's sole lead, explicit model/effort ladder, native-first routing, sandbox-only CLI helper, restricted Claude reviews, and user-directed publication boundary. Do not add default duplicate research sweeps or progress-file polling; use the task's actual research and supervision needs.

The local source's observational turn/token ratios are not causal evidence of savings here. Current prices and model availability were not re-evaluated because no routing change was selected. Local decision checks and dispatch-stub tests establish policy consistency and helper plumbing, not live message delivery, applied effort, worker compliance, or measured cost improvement.

*Adapted: transferred portable task and evidence practices while retaining Codex's execution controls; stopped when the high-impact gaps and counter-cases were covered.*
