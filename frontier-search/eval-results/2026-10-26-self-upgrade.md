# Self-upgrade — 2026-10-26

## Scope and outcome

Nine days after the 2026-10-17 pass. Inputs:
- the runtime delta from Claude Code 2.1.302 to 2.1.311, and from codex-cli 0.163.0 to 0.164.0, checked directly
- a Codex `gpt-6.1-sol` `high` sweep with live search
- two Claude research legs: papers since 2026-10-15, and practitioner write-ups plus the 10-17 pass's unverified leads

The orchestrator read every adopted figure at its primary. Three new scenarios (E23–E25) ran on fresh Claude Opus 5.5 subagents that were not told what was being tested: **3/3 PASS**. There was no full-suite rerun.

## What changed

| Change | Location | Evidence (evidence.md row) | Eval |
|---|---|---|---|
| Trace origin by byline, wire or press-release marker, or citation chain, not wording; state the count of independent origins when agreement carries a conclusion | SKILL.md Sources (Independence) | Evidence Laundering, EMNLP 2026 | E23 |
| An agreeing cluster can crowd out counter-evidence: read at least one source from outside it | SKILL.md Omission check | Evidence Laundering §6.4 (3.48 vs 0.72 correct pages opened) | E23 |
| A snippet or search summary is a lead until its page is opened; before an absence claim, search the text already retrieved | SKILL.md Gap rounds | Retrieved but Not Read 2610.21731; FreekMencke PR #70 | E24 |
| A failed lookup is not an empty one | SKILL.md Stop | pipeshub-ai PR #4070; ORENCloud write-up | E25 |
| With no retrieved support, say so first and lower confidence; noting it while answering normally is the failure | SKILL.md Output | cron-fleet post (8/8 recorded-empty "success"); MIRA #4514 | E25 |
| Runtime 2.1.311: in `-p` and the Agent SDK the search limit counts per turn and resets with each run; the cap notice also rules out browser or computer-use search (2.1.307); robots.txt refusals are normal results recorded as access limits; authenticated pages go through MCP or `gh` | references/runtime.md; evidence.md Runtime facts | tools-reference.md (raw), changelog 2.1.303–2.1.311, live tool schema | E25 (robots.txt and safety-check handling) |
| Sweep pins: re-checked on codex-cli 0.164.0 and Claude Code 2.1.311; the Claude-sweep command ran live; Terra tiers are never pinned (user decision 2026-10-26); per-run `-p` cap wording | references/parallel-research.md | models_cache.json, live `claude -p` run | — |
| Long-MDR row: v3 reinstatement on 2026-10-21, with the first-place claim gone from the abstract | evidence.md | arXiv submission history | — |
| Exa ATLAS: vendor benchmark whose tasks and grader are unreleased | references/sources-research.md | Exa post; exa-labs/benchmarks tree via GitHub API | — |
| Eval method: parallel arms share the search cap; a scenario written with its rule is not held-out evidence | references/MAINTAINING.md | tools-reference (shared cap); ORENCloud; Harness-Delta Attribution 2610.22466 | — |

SKILL.md grew from 10,322 to 10,926 bytes (+5.9%). No rule was cut this pass.

## Eval results

| Scenario | Runner | Result | Notes |
|---|---|---|---|
| E23 — paraphrased cluster | Opus 5.5 subagent, staged fixture | PASS | Traced the four pages to one release through the "statement Tuesday" / BusinessWire / "according to the company" / via-link markers. Opened all three outside sources. Moved from the runner note's "well supported" to "cell-level test data only; 'passed'/'certified' overstates a test method". Kept a quote discrepancy open rather than resolving it. |
| E24 — snippet and silence | Opus 5.5 subagent, staged fixture | PASS | Read the unread half of the docs and the 4.0 notes, and checked the default against raw text. Answered "no by default since 4.0". Labeled the three-retry snippet an unopened 3.x lead. Treated the two owner documents as one origin. |
| E25 — zero-source answer | Opus 5.5 subagent, staged fixture | PASS (second attempt) | The first attempt died on an API safeguard flag (`reasoning_extraction`), probably triggered by a brief asking it to write out "your reasoning"; the retry asked for "trace items relied on and rules applied". The answer opens with "no source retrieved this run says…", reports low confidence, puts the safety check and robots.txt under `Access-limited:`, treats the 404 as one failed URL, and labels the prior-knowledge list unverified rather than using it as the answer. |

Artifacts (session scratchpad, not retained): `evals/e23|e24|e25-{fixture,answer,trace}.md`, `leg-papers.md`, `leg-practitioners.md`, `codex-sweep.md`.

## Sweep diff

The sweep and the legs independently found the same 2.1.307/2.1.311 runtime entries and found no Codex web-search change. That is the same changelog origin, so it confirms the reading but does not corroborate it. The sweep added four items, each read at its primary before adoption: the MIRA and ORENCloud false-success reports and Harness-Delta Attribution (all adopted), and SearchHorizonBench's finding that a consistency stopping rule lost 1.25 utility points after paying for its own probes (consistent with the current gap-based stop; no change). The legs found Evidence Laundering, which the sweep did not surface. The sweep found Kyle Sexton's report of a parent summary that dropped source links (melodic-software/claude-code-plugins #7840), which the legs did not.

## Leads not verified (not in evidence.md)

- **Davenport.** The "24 days of zero-source runs" claim is not in the mirror repo, his site, or his teardown page. The original account is unreadable to non-owners. His code does let a run with zero sources exit 0.
- **Read only by a leg or the sweep, not by the orchestrator:**
  - Self-Consistency of Entity Sets 2610.26421 (citation Jaccard below 0.02 across ten identical runs)
  - Real PMIDs, Wrong Papers 2610.29812
  - Certify 2610.34684
  - Hint-following 2610.32055
  - OpenDS-World 2610.30181
  - Scheduler Is a Hidden Retriever 2610.26310
  - ToolBottleneckBench 2610.21098
  - Ignored, Not Refused 2610.23254
  - NTBench 2610.32531
  - Optimist Deep Research 2610.23299
  - the melodic-software #7840 delivery report
  - Horst Herb's bmlibrarian #292
- **Not yet verified anywhere:**
  - MarkTechPost's Exa 3.0 ATLAS figures
  - Codex issues #55906/#57092: app-server web-search items losing their URL. These do not affect the `exec` sweep, which reads the final message.
  - AUTOPROBE on OpenReview
  - HybridResearcher 2610.24899v2

## Limits

- One sample per scenario. All three are staged fixtures written alongside the rules they test, so they are search-set checks, not held-out evidence (the MAINTAINING note above). No old-skill baseline was run, so the passes do not show the old wording would have failed.
- Retrieved but Not Read reports an association, not a tested cause. Evidence Laundering is a BM25 sandbox. The practitioner false-success reports are single-channel and mostly outside web research.
- The `-p` per-turn search limit is documented in tools-reference.md with no changelog entry. Its introduction version is unknown.
