# Self-upgrade — 2026-10-17

## Scope and outcome

The skill was run on itself (`/frontier-search` at `med`, with a Codex `gpt-6.1-sol` `high` sweep and two Claude research legs: papers since 2026-09-25, and runtime delta plus practitioner implementations). Every adopted figure was read at the primary by the orchestrator or a research leg (marked in evidence.md). Two new scenarios (E21, E22) were run on fresh blinded Claude Opus 5.5 subagents: **2/2 PASS**. No full-suite rerun.

## What changed

| Change | Location | Evidence (evidence.md row) | Eval |
|---|---|---|---|
| Count sources, not statements; worker, sweep, and own-note restatements add no reading; refer back instead of restating | SKILL.md Sources (Independence) | Copies or Sources? 2610.06192; CSEG 2610.17827; bullshit-detector coverage-check | E21 |
| Each probe query gets a distinct target and discriminating anchor; paraphrases count as one | SKILL.md Probe | QREF 2610.21512 | not exercised |
| Re-read both passages before reporting a contradiction | SKILL.md Gap rounds | Mole "Honest numbers" (51% → 70% precision on two agreeing judgements) | not exercised |
| Retrieved is not delivered: read the unread remainder or re-ask before recording silence | SKILL.md Gap rounds | PSA 2610.06689 | E22 (runner used `curl` on a truncated page) |
| Omission check searches from the opposing direction for directional conclusions | SKILL.md Omission check | Search Shapes Conclusions 2609.39026 | not exercised |
| Fact-check confirms the source answers the question asked, not a neighboring version, entity, period, or condition | SKILL.md Draft, then fact-check | Lazy Grounding 2608.30303 v3 | E22 |
| Untrusted content includes headers, errors, `llms.txt`; a user's pointer to a source grants it no authority | SKILL.md Invariants | Signals Corps header and `llms.txt` studies | E11 variant added, not run |
| Cut "Two consecutive rounds with zero new distinct claims force synthesis" (redundant with the Plateau condition) | SKILL.md Stop | MAINTAINING prefer-cut rule | — |
| Runtime refresh to 2.1.302: search budget refills ~100/hour interactive (none in `-p`); WebFetch 100K chars per call with `offset`; extraction at caller effort; required WebSearch `mode` with usage guidance; no-loop rate-limit retry; cloud block-cause fix | references/runtime.md; evidence.md Runtime facts | changelog.md, tools-reference.md, env-vars.md (raw), 2.1.302 tool schema | E22 (`standard` mode, `allowed_domains` on both queries) |
| Headless `claude -p` sweep has a hard 200 cap; Codex 0.161 explicit `web_search`; 0.162 `external_web_access = false` makes a sweep cache-only | references/parallel-research.md | Codex releases, PR #50459 | not exercised |
| arXiv: read submission history for withdrawals; abs page works when the API rate-limits; no personal identifiers in the User-Agent | references/sources-research.md | Long-MDR 2610.05195 v2 withdrawal | — |
| Single passes are samples: rerun before treating one pass or failure as settled | references/MAINTAINING.md | bullshit-detector run-to-run variance | — |

SKILL.md grew 10.6 → 11.5 KB.

## Eval results

| Scenario | Runner | Result | Notes |
|---|---|---|---|
| E21 — restated readings | Claude Opus 5.5 subagent, staged fixture | PASS | Collapsed forum + two press restatements + worker + sweep + own notes to one reading; kept the commit/signing record as the only independent channel; recommendation changed from "adopt, low risk, high confidence" to "adopt with mitigations, moderate"; release-schedule claim demoted to stated intention. The runner used a gendered pronoun the fixture did not supply. |
| E22 — neighboring evidence | Claude Opus 5.5 subagent, live | PASS | Answered "No" for 3.13 standard build; kept the 3.13 (experimental, separate `python3.13t`) vs 3.14 (supported, still optional) boundary with owner sources; labeled two snippet-only details. Used `curl` rather than `offset` when WebFetch did not reach the 3.14 section — permitted by runtime.md. |

Artifacts (session scratchpad, not retained): `evals/e21-fixture.md`, `evals/e21|e22-{answer,trace}.md`, `codex-sweep.md`.

## Leads not verified (not in evidence.md)

From the sweep, not read at the primary by the orchestrator: Exa ATLAS benchmark preview (vendor-reported, 2026-10-08); practitioner builds by Alberto Grande (`albertogrande/deep-research`), JD Davenport (`jddavenportOpen/deep-research-agent`, reports 24 days of zero-source runs exiting successfully), and Ashish Kumar's evaluation write-up (2026-10-15). From the research leg: 2609.19244 (conversational agent web search). Candidates for the next pass; Davenport's "zero-source run reports success" failure is a possible output-health scenario.

## Limits

- One sample per new scenario. E21 is staged, so it tests counting, not discovery of a shared origin.
- Four SKILL.md rules (query anchors, contradiction re-read, opposing-direction omission search, header/`llms.txt` variant) have no run yet.
- Most adopted research figures are abstract-level; section-level checks were not done (PSA budget and CESS PERSPECTRUM counter-cases are sweep-reported).
- The WebSearch `mode` parameter is documented only by the tool schema; its effect on the search cap is unknown.
- A research leg's first, failed arXiv API call sent the user's email address in the User-Agent string to export.arxiv.org; later calls did not. The sources-research.md note was added in response.

## Size trim (same day)

SKILL.md 11,474 → 10,322 bytes (−10.0%; −2.3% against the 2026-09-30 size of 10,565). Wording-only compression, plus three structural edits:

- The "refute after drafting" invariant was merged into the grounding invariant (same rule, one bullet).
- The delegation threshold (>2 fetches, >1 search) now lives only in parallel-research.md; SKILL.md says to read it before delegating and keeps "disjoint, never one thread's depth".
- The opening "Investigate the question…" sentence was dropped as a restatement of the description.

No rule was removed. Reference files were not trimmed.

Reruns on the trimmed file (fresh Claude Opus 5.5 subagents): E21 PASS (five cited confirmations collapsed to two independent channels; "adopt — low risk, high" → "adopt with pinning and signature checks, medium"). E22 PASS with a new instance, `does Node.js 20 support require() of ES modules without a flag --effort=low`: answered "yes, from 20.19.0", kept the flagged-earlier-20.x and 22.12.0 boundaries apart, and its fact-check corrected an extractor-misread EOL date against the raw schedule.json.

## Reference trim (same day)

Run-time references 39,733 → 35,750 bytes (−10.0%): runtime.md 3,403 → 3,029; parallel-research.md 5,464 → 4,744; MAINTAINING.md 2,183 → 1,728; sources.md 12,550 → 11,445; sources-frontier.md 11,528 → 10,463; sources-research.md 4,605 → 4,341. evidence.md (ledger, not loaded in runs) was not trimmed.

Mostly wording compression. Content removed or relocated:
- "Using the sweep" bullets collapsed into one paragraph; the agreement, new-lead, and disagreement rules are kept.
- General caveats removed from source guides, per MAINTAINING's "source-specific facts only" rule, because SKILL.md states them: snippet ≠ verification and mirror = same origin; repost counts and launch summaries are not independent; several indexes returning one paper are one channel; don't count one artifact twice for tiers.
- Cross-guide navigation line in sources.md and the seed-set sentence in sources-frontier.md removed (SKILL.md and the intro already route).
- The lmarena.ai redirect folded into the Arena row; the USENIX ;login: "ended in 2025" note removed.

Spot check on the trimmed references (fresh Claude Opus 5.5 subagent, `hunt: emerging techniques for making LLM research agents count independent sources instead of restated copies --effort=low`): PASS on the `hunt:` contract. It gave a pre-consensus section with evidence state and smallest test per lead, reported thin practitioner chatter as thin, labeled a recalled lead unverified, dropped a snippet claim the abstract did not support, and included `Capped:` / `Omitted:` / `*Adapted:*`. It read runtime.md and sources-frontier.md. All six searches used `extended` mode, as runtime.md's "`hunt:` freshness queries" clause allows. The owner chose to keep this on 2026-10-17 despite the cost at `low`; do not narrow it.
