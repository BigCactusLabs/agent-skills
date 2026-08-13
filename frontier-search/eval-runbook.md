# Frontier-Search Eval Runbook (E1–E9) — Session Handoff

**How to start a new session with this:** open a fresh Claude Code session and say
> "Execute the eval runbook at `<skill-dir>/eval-runbook.md`."

This file is self-contained — it assumes **no memory of the upgrade conversation**.

---

## 0. Why you're doing this

Two goals, in priority order:

1. **Regression test.** The skill was just edited (see §1). Confirm the new behavior actually fires and nothing else broke.
2. **Prune evidence.** Gather data on which SKILL.md rules *never* get exercised across the suite → candidates to cut (the skill's own maintenance philosophy is "a judgment skill degrades by accretion; cut rules real runs never trip"). This is the evidence needed to justify a *cut* to balance recent *adds*.

You are **not** authorized to edit the skill in this session. Produce findings; the owner reviews before any change.

## 1. What changed recently — highest-priority regression checks

Four edits landed. Watch these specifically:

| Change | Location in SKILL.md | Eval that targets it |
|--------|----------------------|----------------------|
| **Revision-regression rule** — re-verify a claim's citation when you displace/revise it; don't disturb grounded neighbors | step 5 displacement guardrail + "Revision regression" failure mode | **E9** (primary), E1 (debate → displacement likely) |
| **Adversarial fact-check** — refute, don't confirm, the top claims | step 8 | **E5** |
| **Existence-vs-faithfulness split** — fabricated URL vs. real-link-no-support are distinct modes | "Misattribution" failure mode | **E5** |
| (Prior turn) revision rule + **E9** scenario added | evals.md | E9 |

If E5 and E9 don't clearly exercise these, that's a **FAIL of the upgrade**, not just a skill miss — flag it loudly.

## 2. Read these first

- Skill instructions: `<skill-dir>/SKILL.md`
- Eval scenarios (the source of truth for `expected_behavior`): `<skill-dir>/evals.md`

Read both fully before running anything.

## 3. Concretize the placeholder queries (do this before running)

E1, E3, E6, E9 have fixed queries — use them verbatim from evals.md. The rest need a concrete instance filled in:

| Eval | Placeholder | Suggested concrete query | Note |
|------|-------------|--------------------------|------|
| **E2** | `<archived/low-activity library>` | `/frontier-search should I adopt Moment.js for a new project` | Moment is officially in maintenance mode and its own docs steer to alternatives — clean test that *archived status IS T2 evidence*. (Backup: the deprecated `request` npm package.) |
| **E5** | "topic where a fact is tempting but unsourced" | `/frontier-search what is the current top score on SWE-bench Verified and which model holds it` | A precise number/date is tempting to fabricate — forces the adversarial fact-check. |
| **E7** | `<SEO-farmed topic with a clear primary>` | `/frontier-search current best practice for password hashing — argon2 vs bcrypt` | Content-farm/listicle saturation vs. a clear primary (OWASP Password Storage Cheat Sheet, Argon2 RFC). Tests `allowed_domains`/`blocked_domains` use, not post-hoc rejection. |
| **E4** | `<niche/new topic, thin chatter>` | *Pick at runtime* — a <2-month-old niche tool or obscure technical claim. **Verify chatter is genuinely thin** before scoring; that thinness IS the test. Time-sensitive, so don't hard-code. |
| **E8** | `<buzzy unproven tool/claim>` | *Pick at runtime* — a currently-hyped tool/claim in `hunt:` mode. Time-sensitive; the frontier moves, so choose fresh. |

Honor the effort flags already in evals.md (E1 `med`, E6 `med`, E9 `high`) and the `hunt:` prefix (E4, E8).

## 4. Execution method

**Recommended — Claude A / Claude B (rigorous).** For each eval, dispatch a fresh subagent (general-purpose, with WebSearch/WebFetch). The subagent must NOT see this runbook or the `expected_behavior` — it just executes the skill, so it can't teach to the test.

Subagent brief template:
> Read `<skill-dir>/SKILL.md` and execute it as the frontier-search skill on this exact query: `<query>`. Honor any `hunt:`/`--effort` in the query. Produce the full output per the skill's output contract. Then append a short **trace**: which source tiers you cited, which named guardrails/failure-mode checks you actually invoked (quote the rule names from SKILL.md), and any `allowed_domains`/`blocked_domains` you used.

Then **you** (orchestrator = Claude A) score the returned output against that eval's `expected_behavior`. The judge must not be the author of the run.

You can dispatch several eval subagents in parallel. **Cost warning:** each is a full research run (multiple web searches + fetches); 9 runs at med/high is real token spend. If scoping down, run the regression-critical four first: **E5, E9, E1, E6**.

**Lighter alternative (quick, less rigorous):** run `/frontier-search <query>` yourself one eval at a time and score after each. Faster, but the judge sees its own work — note this weakens the verdict.

## 5. Scoring — per eval

For each eval, score every `expected_behavior` bullet as **PASS / PARTIAL / FAIL** with a one-line evidence quote from the run. Then an overall eval verdict. Template:

```
### E<n> — <name>   [PASS | PARTIAL | FAIL]
Query run: <exact query>
- <expected bullet 1>: PASS — "<evidence quote from output>"
- <expected bullet 2>: FAIL — <what it did instead>
Notes: <anything notable — wrong shape, missing tier note, padding, etc.>
```

## 6. Prune analysis (goal 2) — the cross-cutting tally

While scoring, keep a tally across ALL runs: for each named rule/guardrail/failure-mode in SKILL.md, did *any* eval exercise it? After all runs, output the list of rules that fired in **zero** evals.

**Be honest about the caveat:** 9 scenarios under-sample a large rule set. A zero-fire rule is a candidate to **either** cut **or** write a new eval for — *not* an automatic delete. Classify each zero-fire rule as:
- **Cut candidate** — redundant with another rule, or guards a failure no eval (and plausibly no real run) would trip.
- **Coverage gap** — a real rule the suite simply doesn't test → propose a new eval instead of cutting.

## 7. What to bring back

A single report with:
1. **Upgrade verdict** — did the four §1 changes demonstrably fire? (E5 adversarial + existence/faithfulness; E9 + E1 revision-regression.) PASS/FAIL each.
2. **Regression verdict** — any eval that FAILed, with the specific behavior gap.
3. **Prune candidates** — the §6 list, each tagged cut-candidate vs coverage-gap, with the under-sampling caveat stated.
4. **Proposed changes** — concrete SKILL.md / evals.md edits (as suggestions, not applied).

Do **not** edit SKILL.md or evals.md. Present for review.
