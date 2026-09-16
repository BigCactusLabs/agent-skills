# Routing history and policy evidence

Read when reassessing routing or the reasons for coordination policy. These notes are historical context, not a runtime dependency, current pricing, or authority to change the user's ladder. Check current primary sources and obtain user authorization before changing routing.

## User decisions and historical observations

The installed skill attributes the Astra-led ladder to user decisions on 2026-09-04, 2026-09-10, and 2026-09-11. Terra was retired on September 11 without new benchmark evidence; Sol remained at `medium`, Astra workers at `low`, and React/component implementation moved to the Claude Opus `high` lane. Preserve those choices unless the user changes them.

Clarification 2026-09-16: this skill is invoked from an existing Astra session, which remains the sole lead. Keep bounded Astra `low` workers; do not create additional orchestrators or ask the user to establish a lead merely to use the skill.

The following claims were moved out of the runtime instructions on 2026-09-16. They were present in the installed skill; their original measurements were not re-audited for this cleanup:

| Historical claim | Scope and limitation |
|---|---|
| One Terra `max` worker spent about 800k output tokens while auto-resuming through four rejected reviews overnight on 2026-09-10. | A single reported incident, confounded by persistence and repair policy; not a comparative model benchmark. |
| Astra `low` emitted about 4k output tokens per task. | Sample size, task mix, and measurement window were not recorded in the installed entrypoint. The former conclusion that this made it the cheapest non-Luna quota rung was unsupported by that observation alone. |
| Sol promotional pricing ran through 2026-11-21. | Historical reminder, not a verified current offer. Verify provider terms before a pricing-based recommendation; do not schedule a task or alter routing from this note. |
| An Opus `high`/`max` comparison recorded Arena Agent Work net improvement of 11.6%/10.4% and P50 cost of $4.07/$5.48, a Text Arena tie, and WebDev scores around 1661/1688, reportedly checked 2026-09-10. | The prior reference pointed to the source Claude skill's `REFERENCE.md`; sample and evaluation details are not reproduced here. These dated figures are not current model rankings or Codex allowance measurements. The existing user gate on `max` remains policy. |

Output counts do not establish backend allowance charges. A shorter entrypoint can improve clarity, but neither its word count nor context caching establishes a quantified quota saving.

## Evidence checked 2026-09-16

The feedback update used a bounded frontier-search pass. These sources inform the scope of the changes; the exact wait cadence, repair caps, and review decisions remain local operating policy.

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Jeremy Hadfield and colleagues, 2025-06-13: a firsthand engineering account of duplicated searches, excessive updates, explicit delegation boundaries, and effort scaled to task complexity. It also reports benefits for parallel research and a need for observability and recovery. This supports reducing duplicate execution while retaining useful evidence collection; it does not prescribe this skill's wait intervals.
- [Towards a Science of Scaling Agent Systems, v3](https://arxiv.org/abs/2512.08296v3), Yubin Kim and colleagues, revised 2026-04-08: the controlled study reports task-dependent coordination effects and greater error propagation without centralized verification. Use it as bounded research evidence for matching coordination to dependencies, not as a benchmark for this skill's current models. The arXiv revision history was checked; independent replication and publication status were not established.
- [Patterns and problems in emerging multiagent systems](https://www.anthropic.com/research/multiagent-systems), 2026-08-13: experiments distinguish useful independent work from difficult interdependent integration and show pathological high-frequency polling. Retain explicit ownership and lead acceptance. The polling experiment is a different system, not direct evidence for a particular Codex cadence.
- [Google Engineering Practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html), retrieved 2026-09-16: review units should be self-contained and conceptually focused; line count alone does not determine size. This is a counterweight to over-batching: a usable milestone may contain several reviewable changes. It does not establish when an AI reviewer can be skipped.

The decision is to remove contradictory busywork incentives, scale records to actual coordination risk, and reserve repeat independent review for material unreviewed risk or unresolved findings. No source establishes universal model efficiency, a quota forecast, or permission to weaken required checks. Coverage included primary guidance, firsthand engineering, and research; no cross-model search sweep was run for this bounded supporting pass.
