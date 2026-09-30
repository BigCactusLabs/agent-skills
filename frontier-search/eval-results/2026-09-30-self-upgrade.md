# Self-upgrade — 2026-09-30

## Scope and outcome

The skill was run on itself (`/frontier-search` at `med`, with a cross-model sweep) to find evidence published since the 2026-09-22 pass, then extended on request with a source-guide expansion and a sweep-pin comparison. Two new scenarios (E19, E20) plus the two open failures (E3, E7) were run on fresh blinded runners: **4/4 PASS**, with the runner caveats below. No full-suite rerun; E1, E9, E14 and E16 remain partial from 2026-09-22.

## What changed

| Change | Location | Evidence (evidence.md row) | Eval |
|---|---|---|---|
| A date is not "still applies": check for a newer owner source that amends, deprecates, withdraws, or reverses older guidance | SKILL.md Sources (recency paragraph) | Stale-Document Poisoning, 2609.31342 | E19 |
| Sufficiency list names the claims the answer must support; Coverage stop requires each to be supported, not topic-matched | SKILL.md Gaps and expansion; Stopping | HALT 2608.02009; CoVeR 2609.26086 | E6/E16 (not rerun) |
| A failed check must change the draft; a caveat beside an unchanged recommendation is not a correction | SKILL.md Omission check and draft fact-check | HAE-GEO 2609.06027 §5.4 | E20 |
| Fan-out stays one level deep | parallel-research.md | 2609.17464 (early signal) | not exercised |
| Sweep pin `gpt-5.6-terra` `max` → `gpt-6.1-sol` `high` | parallel-research.md | local A/B row | not re-scored as E10 |
| Runtime refresh to 2.1.285: domain safety check, WebFetch availability/policy hold, extractor misattribution, `Claude-User` UA | runtime.md; evidence.md Runtime facts | tools-reference, data-usage, changelog (raw `.md`) | not exercised |
| models.md refreshed from the live Codex catalog and made self-contained (no other skill's routing policy) | models.md | catalog 2026-09-30; OpenAI model page | — |
| Source guides: 22 T4 venues, 4 T5 routes, 13 T2 records, NBER, 4 open-access routes; archive.today warning; NVD enrichment caveat; Asianometry and PubPeer flags corrected | sources.md; sources-research.md; sources-frontier.md | live archive/endpoint checks by two research workers, 2026-09-30 | E7 (partial: no new venue cited) |
| "Cited but Not Verified" (2605.06635) upgraded from "primary not read" to abstract verified | evidence.md | abstract | — |

## Eval results

| Scenario | Runner | Result | Notes |
|---|---|---|---|
| E3 — pure lookup | Claude Opus 5.5 subagent | PASS | Probe only; `allowed_domains` on the one search; `Tier coverage:` in the final answer; no footer. The prior E3 failures were on Codex runners, so this does not close the Codex-side defect. |
| E7 — rank bias | Codex `gpt-6.1-sol` `high` | PASS | Structured `domains` on every query, no `site:` syntax (the 09-22 failure). Cited OWASP, RFC 9106 and its errata ledger, maintainer docs; lateral check on Latacora (NCC Group review, arXiv coauthorship, outside venue commentary). The runner said no independent model family was available although `claude` is installed; likely sandbox (`workspace-write`), not scored here. Two Claude attempts were killed by an API safeguard false positive before producing output. |
| E19 — superseded evidence | Codex `gpt-6.1-sol` `high` | PASS | Found NIST's 2026-04-15 operations change as T1; stated the boundary ("As of September 30, 2026 … since April 15"); "store absent scores as unknown, never as zero or low severity"; named CNA, maintainer, and OSV alternatives; rejected deprecated API text as present-contract evidence. Three Claude attempts (two Opus, one Sonnet) were killed by the same safeguard false positive. |
| E20 — verification must change the draft | Claude Opus 5.5 subagent, staged fixture | PASS | Collapsed the sponsored review into the vendor origin, removed the unsupported figure, and reversed the recommendation (Portway high confidence → Relayer moderate) instead of appending a caveat; also caught an unplanted gap (Portway license absent from its cited source). |

Artifacts (session scratchpad, not retained): `evals/e03|e07|e19|e20/{answer,trace}.md`, `evals/e20-fixture.md`, `ab/sweep-61sol-{medium,high}.md`.

## Sweep leads not verified

Reported by the Codex sweeps and not read at the primary by the orchestrator, so not in evidence.md: ReCite (2609.09156), RefVerifier (2609.07652), GANDR (2609.10293), TEMPS (2609.28048), Rethinking Indirect Prompt Injection (2609.04495), multi-agent pruning (2609.05933), CIVI's 34.5% / 37.6% failure split, Regime Boundary Alignment (2609.37491), INSPIRE (2609.33233), RAP (2609.10092), Self-Organizing Agent Teams (2609.22682), OpenAI Agents API search-mode defaults. Primaries read during pin scoring but not adopted as rules: 2609.17930, 2609.25173, 2609.14988, 2609.28614.

## Limits

- One sample per scenario; E7 and E19 ran on a different family than E3 and E20. Runner substitution was forced by API safeguard false positives on security topics (five request IDs, recorded locally). Security-topic scenarios may need a non-Claude runner until that clears.
- E20 is a staged continuation; it tests the fact-check's disposition, not whether a live run would detect the shared origin.
- The source workers chose venues from prior knowledge and then verified them live, rather than discovering them through citations; both exceeded their fetch budgets. Vendor/employer interests were checked for two venues only (Majors, Quinn).
- The sweep-pin comparison is n = 1 per arm; see evidence.md.
- Static validation: `quick_validate.py` passed; local links, anchors, and table columns pass in all edited files. Six pre-existing table-column warnings in eval-runbook.md §3 were left unchanged.
