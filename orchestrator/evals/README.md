# Opus effort-tier evals

Also used for a Codex arm on 2026-09-30 (`run_codex_eval.py`, section at the end): GPT-6.1 Sol `xhigh` vs GPT-6 Astra `low` on the same implementer cases.

Empirical check of the effort ladder used by the Opus 5.5 roles in this repo:
`implementer-opus-med` (medium) -> `implementer-opus-xhigh` (retry), and
`pr-reviewer-med` (medium) -> `pr-reviewer-xhigh` (retry) -> `pr-reviewer-max` (user-gated).
The orchestrator docs (`~/.claude/skills/orchestrator/`) record the current tiering; the numbers
in `results/` are the evidence behind it.

## What is published

This directory holds the evidence, not the harness: this README, `report.py`, and `results/*.jsonl` stripped to per-run aggregates (cost, wall time, turns, tokens, pass or recall verdict, finding counts, effort verification). Reports, transcripts, diffs, judge evidence and the fixture set stay unpublished because they quote fixture code, and one fixture repo is private; its cases appear as `private-<n>`. The scripts named below are described so the method is reviewable. Regenerate every table with `python3 report.py implement` and `python3 report.py review`; the Codex arms with `python3 report_codex.py`.

## Layout

Code and small data live here and are committed. Large, regenerable state lives outside the
repo because Claude Code registers any frontmatter `.md` found in a subdirectory of
`~/.claude/agents/` as an agent, and the fixture clones contain such files.

| path | what |
|---|---|
| `validate_fixtures.py` | Mines bug-fix commits from local repo clones (root path set in the script) into SWE-bench-style fixtures: base = parent commit, hidden tests must fail before the fix and pass after. Writes `fixtures.json`. |
| `build_review_fixtures.py` | Blames the lines each fix removed to find the bug-introducing commit; clones the repo at that commit as a reviewer fixture. Writes `review_fixtures.json`. |
| `make_cases.py` | Turns fixtures into orchestrator-shaped briefs (`cases.json`): 15 implement cases, 8 review cases. |
| `run_eval.py` | Runs a role headlessly at a given effort, verifies the applied effort from the session transcript, grades implementer runs against the hidden tests, saves reviewer reports. Appends to `results/<suite>.jsonl`; resume-safe by `case|effort|rep`. |
| `grade_review.py` | Judge pass over reviewer rows with `claude-fable-5-1` (a different model from the one under test). Structured output: recall of the planted defect (found / partial / missed) and per-finding validity. |
| `report.py` | Per-effort tables, per-case paired table, retry-ladder view, change-size and scope-churn columns. |
| `run_codex_eval.py` | Codex arm: same fixtures, briefs and grader, driven by `codex exec -m <model> -c model_reasoning_effort=<effort> --dangerously-bypass-approvals-and-sandbox --json`; verifies model and effort from the session rollout; halts on a rate-limit error. Appends to `results/codex-implement.jsonl`, keyed `case|model|effort|rep`. |
| `report_codex.py` | Per-arm table, cost per success, per-case grid for the Codex rows. |
| `wiring_check.py` | Free oracle/null check of the implementer grader. Run it after touching fixtures or the grader. |
| `results/` | Raw rows. Every headline in a report is recomputed from these. |
| `case_dump.md`, `*.log` | Fix/test diffs used to author briefs, and pilot logs. |
| `$AGENT_EVAL_DATA` (default `~/.cache/claude-agent-evals/`) | `fixtures/`, `mirrors/`, `runs/`. About 16 GB. Rebuild with `validate_fixtures.py` then `build_review_fixtures.py`. |

## Method notes

Every run passes `--effort` explicitly and asserts the level from the transcript, because
`claude -p --agent <role>` does not apply the role's `effort:` frontmatter (measured 2026-09-27,
claude-code 2.1.283). The in-session Agent tool does honor it, so production dispatch is unaffected.

## Reading the numbers

- Implementer pass is end-state: all FAIL_TO_PASS and PASS_TO_PASS tests pass after the hidden
  tests are overlaid. The agent never sees the hidden tests.
- Reviewer recall is judged, not string-matched. Read `judge.recall_evidence` before trusting a
  call. The judge has so far marked almost no findings invalid, so treat precision as an upper bound.
- With 15 and 8 cases at 2 reps the noise floor is about 14 points per arm. The design resolves
  gross gaps and cost or latency ratios, not 5-point differences.
- The ladder view answers the operative question: medium first, xhigh only on failure, versus a
  flat higher effort.

## Reviewer full matrix (2026-09-27)

Rep 2 at medium, high and xhigh plus max on the remaining 6 cases: 30 more runs ($56 + $26
judge), bringing the reviewer suite to 56 rows, 16 per effort and 8 at max. Every row's effort is
verified from its transcript.

Planted-defect recall over 8 cases x 2 reps (max: 8 cases x 1 rep):

| effort | found | partial | missed | findings/run | invalid | mean $ | median wall | worst wall |
|---|---|---|---|---|---|---|---|---|
| medium | 7 | 7 | 2 | 8.9 | 2/120 | $0.71 | 3.1 min | 9.3 min |
| high | 6 | 8 | 2 | 10.2 | 3/126 | $1.04 | 4.9 min | 13.6 min |
| xhigh | 9 | 6 | 1 | 13.3 | 5/148 | $2.21 | 8.5 min | 14.8 min |
| max (n=8) | 4 | 4 | 0 | 14.5 | 5/81 | $4.16 | 17.8 min | 40.9 min |

Rep 2 reversed the slice's medium result: medium found 2/8 in rep 1 and 5/8 in rep 2, and gave the
same verdict on only 4/8 cases across reps (high 6/8, xhigh 6/8). The rep 1 ordering was run-to-run
noise. On found-rate no effort separates from another (Fisher exact, medium vs xhigh p=0.72, high
vs xhigh p=0.48). What does separate is the floor: found-or-partial is 14/16 at medium and high,
15/16 at xhigh, 8/8 at max. Misses: medium missed two different cases once each, high missed
the same case (private-1) in both reps, xhigh missed once, max never. High matches medium
on every recall count at 1.5x the cost. Findings per run and cost rise
monotonically with effort; recall does not.

Ladder view over the 16 (case, rep) pairs, escalating when the first rung did not report the
defect as found:

| policy | found | found-or-partial | $ / case |
|---|---|---|---|
| flat medium | 7/16 | 14/16 | $0.71 |
| flat high | 6/16 | 14/16 | $1.04 |
| flat xhigh | 9/16 | 15/16 | $2.21 |
| medium -> xhigh | 10/16 | 16/16 | $1.89 |
| medium -> high | 8/16 | 15/16 | $1.25 |
| high -> xhigh | 10/16 | 16/16 | $2.38 |

medium -> xhigh matches or beats flat xhigh on both recall counts at 15% less cost, and the
high rung adds nothing that xhigh does not add for the same escalation. Max found 4/8 against
xhigh's 9/16 on the same cases at 1.9x the cost and 2x the wall time, with the slowest run at 41
minutes. The data support the current ladder (medium default, xhigh retry, max gated) and the
retirement of `pr-reviewer-high`; they do not support making xhigh the default.

Caveat: the escalation trigger in this table is the judge's verdict, which the orchestrator does
not have. In production the retry fires on the orchestrator's read of the review, so the ladder
numbers are an upper bound on what medium -> xhigh delivers.

## One-third slice (2026-09-27)

Rep 1 of every case at medium, high and xhigh; max only on the 2 pilot cases. 45 implementer
runs ($45) and 26 reviewer runs ($41 + $23 judge). Every row's effort verified from its transcript
(`run_eval.py <suite> --reverify` backfills the check if the transcript lookup ever fails).

Implementer, 15 cases: 14/15 pass at medium, high and xhigh. Mean cost $0.59 / $0.84 / $1.60,
median wall 1.6 / 2.6 / 5.3 min, median turns 11 / 12 / 33. Zero scope churn at every level.
The one failure (dl-readme-blob) fails identically at all three efforts on a pre-existing test
whose expectation the reference fix changed without the brief saying so (fenced-code handling);
it carries no effort signal. Effort bought nothing on this suite; the medium -> xhigh ladder
never escalated because medium never failed a solvable case.

Reviewer, 8 cases, planted-defect recall (found / partial / missed):

| effort | found | partial | missed | findings/run | mean $ | median wall |
|---|---|---|---|---|---|---|
| medium | 2 | 4 | 2 | 8.4 | $0.71 | 3.1 min |
| high | 3 | 4 | 1 | 9.6 | $1.08 | 5.1 min |
| xhigh | 4 | 3 | 1 | 13.6 | $2.14 | 8.3 min |
| max (n=2) | 1 | 1 | 0 | 16.0 | $4.54 | 19.9 min |

Superseded by the full matrix above: rep 2 moved medium from 2/8 to 5/8 found, so the monotonic
ordering seen here was noise. Cost roughly doubles per rung. Judge marked 4 of 208 findings
invalid, so precision is still an upper bound.

## Pilot (2026-09-27)

Implementer, 3 cases: 9/9 pass at medium, high and xhigh. Mean cost $0.52 / $0.59 / $1.45,
median wall 1.3 / 2.6 / 4.9 min. No scope churn at any level.

Reviewer, 2 cases: planted defect found 0/2 at medium and high, 1/2 at xhigh and max (the other
run partial at xhigh and max, missed at medium and high). Mean cost $0.85 / $1.22 / $2.87 / $4.54,
median wall 3.5 / 5.3 / 11 / 20 min.

## Codex arms: GPT-6.1 Sol xhigh vs GPT-6 Astra low (2026-09-30)

Paired run of the 15 implementer cases, one rep, the same briefs and hidden tests as the Opus
rows, driven by `codex exec` with approvals and sandbox bypassed in a fresh fixture copy. Model
and effort are asserted from every session rollout. Cost is OpenAI list price computed from the
reported usage (output tokens taken to include reasoning); credits follow the Codex rate card
(6.1 Sol 50 / 2.5 / 250, Astra 250 / 25 / 1,250 per Mtok input / cached / output).

| arm | pass | mean $ | mean credits | cost / success | median wall | median commands | mean output tokens |
|---|---|---|---|---|---|---|---|
| gpt-6-astra low | 14/15 | $1.07 | 26.7 | $1.14 | 2.9 min | 12 | 3.7K |
| gpt-6.1-sol xhigh | 14/15 | $0.32 | 7.9 | $0.34 | 9.0 min | 22 | 10.9K |

Both arms miss the same case (dl-readme-blob), the brief-gap case every Opus 5.5 effort also
missed; it carries no model signal. Source diffs match per case within a few lines; 6.1 Sol writes
about 1.5x the test lines and runs about twice the shell commands. The slowest 6.1 Sol run took
25.6 minutes (62 commands) against Astra's 6.7 minutes on the same case. No run failed, hit a rate
limit, or raised an approval or auto-review item. Same caveats as above: n = 15 at one rep resolves
gross gaps and cost ratios, not small recall differences, and hidden-test grading is a machine
check standing in for review-caught acceptance. 6.1 Sol `high` and `medium` were not measured.

