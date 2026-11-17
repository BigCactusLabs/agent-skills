# Model routing

Read before choosing a tier for a dispatch and before stepping one after a failure. `SKILL.md` carries the ladders and the user gates in short form so they survive compaction; this file is the full table and the reasoning. A rung change edits both. Benchmark basis for every row: `REFERENCE.md` (tier-routing evidence). Codex ids: `gpt-6-luna`, `gpt-6.1-sol`, `gpt-6-astra`.

## Roles and rungs

| Role | Model | Notes |
|------|-------|-------|
| Orchestrator | Session model (you) | Specs, review, merges: never delegated |
| Claude scouts | `Explore` (inherits, capped at Opus); `scout-sonnet` (sonnet `high`) for recon that reuses session context or needs Linear / Google Drive / Claude Docs reads (its MCP allowlist) | Context-free recon goes to luna; other MCP recon → `general-purpose` at `model: sonnet` |
| Claude implementers | `implementer-opus` at its default `medium` for every coding leg | Retry: the same role with `effort: "xhigh"` on the call, which is also the first rung for all React / component work (user decisions) |
| Claude reviewers | `pr-reviewer-opus` at its default `medium` for every review, silent-failure domains included; also plans, specs, and uncommitted changes the brief names | Retry, or a review you judge needs more depth: `effort: "xhigh"`. `effort: "max"` is **user-gated**: WebDev / visual-refinement review only |
| Claude researchers | `researcher-opus` at its default `medium` for fact-gathering whose answer shape is known (lookups, figures, versions, pricing); `effort: "high"` for decision-grade synthesis across conflicting sources | Preloads frontier-search. The brief names its frontier-search `--effort` budget (default `med`), return shape, and report path |
| Codex recon, lookups, mechanical write work | luna @ `max` | Enumerable grind and any leg passing the latitude test. 6.1-sol `medium` is the retry, and the first rung for web synthesis |
| Codex implementers (machine-caught) | 6.1-sol @ `medium` | Fails the latitude test but has a mechanical check; short mechanical test/build loops. Any failure → resume the thread first, then 6.1-sol `xhigh` (depth failure) or astra `low` (conceptual failure) |
| Codex implementers (review-caught) | 6.1-sol @ `xhigh` | First rung when a failure lands on your review, outside silent-failure domains. Retry: astra `low`, then astra `high` |
| Codex terminal-heavy loops / probe | astra @ `low` | Build/test/fix loops where wall time dominates, and the retry rung after 6.1-sol `xhigh`. Retry: astra `high` |
| Codex hard cases | astra @ `high` | Multi-subsystem or silent-failure-domain legs from the start; cross-model review outside silent-failure domains; retry after astra `low` |
| Codex judge / hard repair / untrusted input | astra @ `xhigh` | Single-turn legs where the judgment *is* the deliverable: silent-failure-domain first-round review, repair after a hard-case leg failed once, untrusted content. Never a bulk worker |
| Docs sync | luna @ `max` or `docs-sync-sonnet` | A doc made stale by a change is fixed *in that same change* (user policy), triggered by a changed instruction or contract, not every checkpoint; milestone status lives in one record. Tiny edits stay local; luna when the diff/spec states the content, `docs-sync-sonnet` when it needs session context or MCP |

## Ladders and stepping

Codex: luna `max` → 6.1-sol `medium` → 6.1-sol `xhigh` → astra `low` → astra `high` → astra `xhigh` (single turn). Claude: sonnet `high` (recon, docs sync) · opus `medium` → `xhigh` for implementers and reviewers alike, one role per job with the rung set by the call's `effort`. Anything not on a ladder is off it (user decisions, recorded in `AUDIT.md`). `max` on astra or sol, `ultra` anywhere, and opus `max` need explicit user permission per dispatch. Pick the cheapest rung expected to pass first try: under-provisioning costs one retry, over-provisioning costs every dispatch. Astra and luna legs stay under their 272K Codex window (chunk instead); 6.1-sol has 500K.

- **The starting rung is set by who catches a failure, not by difficulty** (the Codex implementer rows above); Claude starts every coding leg at opus `medium`. Steady state: cheap scouts of both families feeding one expensive judge.
- **Which way to step:** a *conceptual* failure (wrong strategy, missed constraint) moves **model tier**; a *depth* failure (strategy right, one hard piece left) moves **effort** one rung (on 6.1-sol that is `medium` → `xhigh`; `high` is not a rung).
- **Exits before any tier change:** *harness defect* → repair the brief, same tier; *ran out of runway* (approach sound, tests improving) → resume the same worker, since persistence is cheaper than a model swap; *contested* → Claude judgment; rate-limit/quota → halt.
- **One lead.** Astra never gets peer orchestrator authority (its price as a session lead, and no cross-family control plane); a Codex lane lead that fans out internally is a watch item, not a row (`REFERENCE.md`).
- **Cost.** Cheapest *adequate* tier across both families; load-balance toward the pool with headroom; neither engine is the default (rates converged tier-for-tier, `REFERENCE.md`). Haiku is banned (user policy).

## Luna latitude test

The luna/sol boundary is verifiability, not difficulty. Luna is ~20× cheaper than sol, so luna-first-with-sol-retry wins whenever luna's first-try pass rate clears ~5%, *provided a failed attempt is caught by a machine, not your review*. Three questions per leg:

1. Is the acceptance check mechanical and cheap (tests, build, lint, schema, diff shape)?
2. Is the output fully determined by the spec (pattern application, not design)?
3. Are failures loud (compile/test errors) rather than silent (subtle logic, cross-file invariants, concurrency, persistence, security)?

Three yeses → luna @ `max`, write work included: codemods, rename/import sweeps, enumerated bulk edits, scaffold-from-template, lint/format/snapshot loops, test-grind with a known fix class, log-digging, data extraction, doc-sync from a source of truth. Any "no" → off luna from the start, per the table.

## Research legs

Codex gets search legs whose answer shape is known in advance; open-ended discovery stays with Claude (frontier-search posture in every research spec). Decision-grade research defaults to **dual-track triangulation**: a background Codex sweep diffed at synthesis.

## Diagnosis legs

For a root cause that is unclear, with two or more hypotheses still live. One investigator tends to stop at the first plausible explanation, and later investigation is biased toward it ([agent teams docs](https://code.claude.com/docs/en/agent-teams#investigate-with-competing-hypotheses), which give the argument and no measurements). The docs' remedy is teammates that message each other. Here the same structure runs through the lead in two rounds, which keeps the read-only roles' `main`-only message rule and avoids the team cost.

1. **Enumerate** two to four hypotheses that predict different observations. With one hypothesis this is an ordinary scout leg; with a deterministic reproduction it is a bisect or failing-test leg for Codex.
2. **Round one:** one read-only leg per hypothesis, in parallel, tiered by the table above (luna when the check is enumerable and context-free, `scout-sonnet` when it reuses session context). Each brief names one hypothesis and asks for the evidence for and against it by path and command, plus the observation that would refute it. Each leg reports to its own file and is not told which hypothesis you favor.
3. **Round two:** resume each leg (`SendMessage`, or helper `action: resume`) with the paths of the other reports. It runs the refuting checks those reports name, says which hypotheses it could not refute, and says whether its own survives. Agreement without a check run is not evidence: review protocols fell into false consensus until disagreement had to be explicit and grounded (`REFERENCE.md`, review and repair evidence).
4. **Rule (you):** accept a cause when a leg other than its proponent looked for its refuting observation and did not find it. Otherwise record the diagnosis as undetermined, with the cheapest check that separates the hypotheses left. The fix is a separate implementation leg under the usual routing.

The legs count against the 3–5 concurrency limit. Unmeasured here: the fan-out evidence in `REFERENCE.md` (tier-routing evidence) covers short closed tasks, so use this for diagnoses and not as a default for recon.
