# Frontier-search targeted fixes — 2026-09-22

Status: **approved patch applied; E7 PASS carried forward; E3 remains unaccepted**. Luna generation 3 passes the round/footer checks but omits final Tier coverage. A same-snapshot Sol medium diagnostic supplies the note and no footer but uses an expansion before the required freshness conflict. All workers have ended; no further skill edits were made. This follows the [original suite](2026-09-22-orchestrated.md); its dated results remain unchanged.

## Changes

- The existing source-filter instruction now gives Codex's `search_query[].domains`, Claude's `allowed_domains`/`blocked_domains`, hostname-only values, and a valid `site:example.com` fallback when structured filtering is unavailable.
- The short Answer format now explicitly includes the existing `Tier coverage:` requirement when fewer than three tiers are cited.
- Pure fact lookups now resolve in the probe, with at most one expansion to reconcile a fresher conflicting source.
- Pure fact lookups explicitly omit the Adapted footer. E3 exposed a conflict between the general expansion-footer instruction and its pre-existing no-footer expectation.

Four locations in SKILL.md changed for the two evals: the filter paragraph, probe lookup limit, Answer contents, and lookup footer exception. Current entrypoint: 13,326 bytes, up 335 from the compacted 12,991 and still 73.9% below the original 51,081. Subsequent wording changes address observed residuals below. No other research rule, reference or eval expectation was changed.

## Validation method

Fresh blinded runners execute the same E3 and E7 queries, models and contract as the original suite against a frozen updated skill. They receive no prior answer, defect, expected behavior or proposed fix. Root Astra judges the artifacts. E3 requests Luna max; E7 requests Astra low. Actual native runtime model/effort is not exposed; model labels below refer to requested settings. E7 has two fresh generations; E3 has three on Luna, each following an intervening wording change, plus one unchanged-snapshot Sol medium fallback diagnostic. Earlier results remain below. This is not an unchanged rerun until success or a matched statistical comparison.

First fix snapshot (E3 and E7 generation 1), SKILL.md SHA-256: `6d4c31d5806dae702dc350ae1cbce64df23e6e59a6ccdea32c3a8fe31054e2f2`.
Evidence root: `<run-dir>`; manifest records task lifecycle, exact artifact paths, source hashes and requested settings. The inherited contract requests saved drafts/traces, so instrumentation limits still apply.

Static checks: `quick_validate.py` exited 0 (`Skill is valid!`); all 17 local skill/reference links resolve; whitespace clean; lead reviewed each focused diff. Validation uses the live tool schema for the Codex filter name and the existing Claude runtime reference for its filter fields. This directory is not a Git repository; no Git mutation was performed.

## E3 — FAIL on Luna generation 3; earlier results retained

Generation 1: the final answer includes `Tier coverage: T1 primary artifacts and T2 project release authority; T3–T5 were unnecessary for this pure version lookup.` It uses one justified freshness expansion, but adds an Adapted footer. This fails E3's existing no-footer requirement. The skill's general footer-after-expansion instruction conflicted with that requirement for a freshness check. The final revision explicitly omits the footer for a pure lookup resolved in the probe or one freshness-verification round.

The first trace also uses site operators despite structured filtering being available; this predates the tighter every-query wording in revision 2. No first-generation full pass is claimed.

Generation 2: the final answer again includes the correct Tier coverage note and supports the Current/LTS distinction with official sources. Its trace records one probe plus **two** expansions, and the final answer has an Adapted footer. Both violate the existing E3 expectations (at most one freshness-conflict expansion; no footer). The factual result and the requested missing-note fix pass; the full scenario does not. The footer exception added for probe/one-round lookups does not address a runner that takes two rounds.

The remaining contract gap is that the skill's generic medium budget still applies to fact lookups; its short-answer depth is a shape guide rather than an explicit lookup-round limit. The user then approved the specific limit and unconditional pure-lookup footer exception shown below; they are now applied.

Revision 3 SHA-256 (generation 2): `d4bfa719f92b0c5fef643e4ee700e92ede86ea2b7ba88e40fdd28955a3965f08`.

Generation 3: **FAIL**. One targeted freshness expansion, supported version answer and no Adapted footer pass. The final answer omits Tier coverage again; the trace contains it. This is the original missing-note defect recurring on the final skill, not a complete closure. The domain-targeted searches use structured filters.

Final tested candidate SHA-256: `06af394935664eeec579b2de6e2bd2c427e09613b6eb69c7d4813fa3e9b4db4e`.


Query: `/frontier-search what is the current stable version of Node.js`

## E7 — PASS on generation 2

Generation 1: the required domain-filter mechanism was observed in all four probe searches and the omission search. Two later queries still used invalid `site.tobtu.com` / `site.latacora.com` syntax without filters. Accepted as partial closure, not a clean fix. The same sentence was then tightened to require structured filters on **every domain-targeted query**; a fresh blinded runner checked the unchanged query against that revision.

Generation 2: all three domain-targeted searches use structured hostname filters (OWASP, RFC Editor and IETF). The fourth query is deliberately broad for the counter-case and has no domain restriction. No site operators or malformed domain syntax appear. Primary guidance and named practitioner counter-cases support the final answer; an unfamiliar venue and farm-only outcome were not encountered. The mechanism and the residual syntax defect both pass this sample.

E7 remains valid for the final snapshot: the later changes only affect pure-lookup rounds and footers, which do not apply to this algorithm comparison. All relevant E7 instructions are unchanged.

Generation 2 snapshot SHA-256: `01c1c05a157c7f77a8a2e1e9f8ebdb19dcccb69262e190bf19a79e271b3b5dab`.


Query: `/frontier-search current best practice for password hashing — argon2 vs bcrypt --effort=med`

## Limits

Only E3 and E7 rerun. The prior partials E1/E9/E14/E16 retain their coverage limits; four replay passes remain separate. No claim of a full 17-scenario rerun or general reliability improvement follows from these samples. Claude-specific runtime behavior and E7's unfamiliar-venue/farm-only conditional variants require separate coverage when applicable.

## Approved checkpoint continuation

The first four worker generations ended and were collected. Their evidence remains intact. The user replied “yes” to applying the prepared patch and rerunning E3. That fifth worker generation has completed and failed only the Tier coverage output requirement. A sixth bounded worker used the orchestrator’s Luna-to-Sol fallback on the unchanged snapshot, with no implementation changes. It also completed; its separate diagnostic result is below.

The invoked codex-orchestrator skill requires a user checkpoint after the second rejected repair review. The first tested revision retained E7 syntax/E3 footer defects; the final tested revision still fails the full E3 scenario. The user checkpoint now covers that reviewed snapshot and the exact follow-up patch. Counters and historical findings are preserved.

Approved patch (applied exactly; Luna E3 result above):

```diff
--- a/SKILL.md
+++ b/SKILL.md
@@ -78,6 +78,8 @@
 
 ### 1. Probe
 
+For pure fact lookups, resolve in the probe; allow at most one expansion only to reconcile a fresher conflicting source.
+
 Decompose into sub-questions, including the strongest counter-question for decisions, debates, and comparisons. Spread probes across sub-questions and tiers using domain filters; batch where supported. At `med`/`high`, reserve one probe for an oblique angle or unexpected community; it may find nothing.
 
 At probe time, consider an independent cross-model sweep under [parallel-research.md](references/parallel-research.md): applicable at `high` or decision-oriented `med`, only when permitted and a different model family is available. Skip silently at `low`, for pure lookups, or without an independent engine.
@@ -138,7 +140,7 @@
 
 Include a pre-consensus section for `hunt:` at any depth. Report thin/stale evidence without padding. Use `Capped:` if budget ends before convergence and suggest higher effort when available. Include `Tier coverage:`, `Access-limited:`, and `Omitted:` where applicable.
 
-After expansion, finish with one short `*Adapted: <reason>.*` clause describing strategy or stopping. Disclose promotion or narrowing there. Omit the footer for pure lookups resolved in the probe or one freshness-verification round. Keep process narration out of the final opening; brief progress updates during long runs are welcome.
+After expansion, finish with one short `*Adapted: <reason>.*` clause describing strategy or stopping. Disclose promotion or narrowing there. Omit the footer for pure fact lookups. Keep process narration out of the final opening; brief progress updates during long runs are welcome.
 
 ## Maintenance
 
```

Applied after user approval; rerun only E3. E7 carries forward because neither change affects domain filtering or non-lookup answers. The complete proposal is also saved at `<run-dir>/proposed-lookup-fix.patch`.

Evidence:

- Task manifest (`<run-dir>/state.json`)
- E3 generation 3 answer (`<run-dir>/results/e03-g3/answer.md`) and trace (`<run-dir>/results/e03-g3/trace.md`)
- E7 final answer (`<run-dir>/results/e07-g2/answer.md`) and trace (`<run-dir>/results/e07-g2/trace.md`)

Raw evidence is in temporary storage; this durable report preserves the rulings and proposed patch. The original full-suite report and eval definitions are unchanged.

## Same-snapshot Sol medium diagnostic

**PARTIAL; full E3 not accepted.** One fresh blinded worker received the identical query, contract and final skill with Sol medium requested instead of Luna max. No source edit or rubric disclosure occurred.

- Final Tier coverage: PASS; explicitly lists T1/T2 and explains skipping T3–T5.
- No Adapted footer: PASS.
- At most one expansion: PASS for count.
- Expansion only for a fresher conflicting source: FAIL. The trace says “one targeted confirmation round used to make the primary artifact evidence explicit” and “No conflict found.” The fresher release appeared only in post-draft checking, so it does not retroactively justify the earlier confirmation round.
- Source-filter adherence: additional deviation; one site-targeted query omitted the available structured filter. The first three probes used real filters. The query's `site:` syntax was valid; it violated the instruction to use structured filtering when available.
- Draft check: materially corrected the stale release number before finalization, preserving LTS guidance. No unsupported version carried into the final answer.

This tests another permitted runner on one sample. It does not prove a model-specific cause or convert the failed Luna run to a pass. Diagnostic answer (`<run-dir>/results/e03-sol-diagnostic/answer.md`) and trace (`<run-dir>/results/e03-sol-diagnostic/trace.md`).

## Final disposition

The exact approved patch is installed and static validation passes. E7's prior pass carries forward because only pure-lookup behavior changed. E3's required behavior is explicit in the skill but still inconsistently followed by the observed runners. Do not label E3 fixed or the complete suite passed. The three corrective retries are now used; the next implementation attempt requires another user checkpoint under codex-orchestrator. No additional patch is proposed or silently applied. All six worker generations have ended and their reports are collected.

