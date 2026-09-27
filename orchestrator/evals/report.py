#!/usr/bin/env python3
"""Summarize results/*.jsonl by effort level. Recomputes every headline from raw rows.

  report.py implement    pass rate, cost, wall time, turns, cost per success, paired per-case table
  report.py review       recall (found/partial/missed), findings, precision, cost, judge cost
Prints markdown; --json dumps the aggregates."""
import json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = ["low", "medium", "high", "xhigh", "max"]


def rows_for(suite):
    f = ROOT / "results" / f"{suite}.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 2) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def out_tokens(r):
    u = r.get("usage") or {}
    return u.get("output_tokens")


FIX = {(f["repo"], f["fix_sha"]): f for f in json.loads((ROOT / "fixtures.json").read_text()) if f.get("status") == "ok"} if (ROOT / "fixtures.json").exists() else {}
CASE = {c["id"]: c for c in json.loads((ROOT / "cases.json").read_text())["implement"]} if (ROOT / "cases.json").exists() else {}


def src_lines(r):
    d = r.get("diff") or {}
    return (d.get("src") or {}).get("add", 0) + (d.get("src") or {}).get("del", 0) if isinstance(d.get("src"), dict) else None


def extra_src_files(r):
    """Non-test files touched that the reference fix did not touch (scope churn)."""
    d = r.get("diff") or {}
    c = CASE.get(r["case"]); fx = FIX.get((c["repo"], c["fix_sha"])) if c else None
    if not fx or not isinstance(d.get("files"), list):
        return None
    ref = set(fx["src_files"]) | set(fx.get("other_files") or [])
    return sum(1 for f in d["files"] if f not in ref and not (d.get("test") and f in fx.get("test_files", [])) and not any(t in f for t in ("test",)))


def implement(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["effort"]].append(r)
    print("| effort | runs | pass | pass rate | errors/timeouts | effort verified | median $ | mean $ | $ per success | median wall min | median turns | median out tok | median src lines | runs w/ extra src files |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    agg = {}
    for e in ORDER:
        rs = by.get(e)
        if not rs:
            continue
        n = len(rs); p = sum(1 for r in rs if r.get("pass"))
        costs = [r.get("cost_usd") for r in rs]
        cps = round(sum(c for c in costs if c) / p, 2) if p else None
        agg[e] = {"n": n, "pass": p, "rate": p / n, "mean_cost": mean(costs), "cps": cps}
        print(f"| {e} | {n} | {p} | {p / n:.0%} | {sum(1 for r in rs if r.get('is_error'))}/{sum(1 for r in rs if r.get('timeout'))} | "
              f"{sum(1 for r in rs if r.get('effort_verified'))}/{n} | {med(costs)} | {mean(costs)} | {cps} | "
              f"{med([(r.get('wall_s') or 0) / 60 for r in rs])} | {med([r.get('num_turns') for r in rs])} | {med([out_tokens(r) for r in rs])} | "
              f"{med([src_lines(r) for r in rs])} | {sum(1 for r in rs if extra_src_files(r))}/{n} |")
    # paired per case
    cases = sorted({r["case"] for r in rows})
    efforts = [e for e in ORDER if e in by]
    print("\nPer case (pass count / reps, mean $):\n")
    print("| case | " + " | ".join(efforts) + " |")
    print("|---|" + "---|" * len(efforts))
    for c in cases:
        cells = []
        for e in efforts:
            rs = [r for r in rows if r["case"] == c and r["effort"] == e]
            if not rs:
                cells.append("-"); continue
            cells.append(f"{sum(1 for r in rs if r.get('pass'))}/{len(rs)} (${mean([r.get('cost_usd') for r in rs]) or 0:.2f})")
        print(f"| {c} | " + " | ".join(cells) + " |")
    # retry-ladder view: medium then xhigh on failure, vs flat
    if "medium" in by and "xhigh" in by:
        print("\nLadder view (per case, rep 1): medium first, xhigh only if medium failed")
        tot_cost = 0; solved = 0; n = 0
        for c in cases:
            m = next((r for r in rows if r["case"] == c and r["effort"] == "medium" and r["rep"] == 1), None)
            x = next((r for r in rows if r["case"] == c and r["effort"] == "xhigh" and r["rep"] == 1), None)
            if not m or not x:
                continue
            n += 1
            cost = m.get("cost_usd") or 0
            ok = bool(m.get("pass"))
            if not ok:
                cost += x.get("cost_usd") or 0; ok = bool(x.get("pass"))
            tot_cost += cost; solved += ok
        if n:
            print(f"  cases={n} solved={solved} ({solved / n:.0%}) total ${tot_cost:.2f}, ${tot_cost / n:.2f}/case, ${tot_cost / max(solved, 1):.2f}/success")
    print("\nStatus lines / errors:")
    for r in rows:
        if not r.get("pass"):
            print(f"  {r['key']:38s} {str(r.get('status_line'))[:60]:60s} {str(r.get('error') or '')[:80]} f2p={((r.get('grade') or {}).get('f2p_passed'))}/{((r.get('grade') or {}).get('f2p_total'))} newfail={len((r.get('grade') or {}).get('new_failures') or [])}")
    return agg


def review(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["effort"]].append(r)
    print("| effort | runs | judged | found | partial | missed | recall (found) | findings/run | valid | invalid | precision | effort verified | median $ | mean $ | median wall min | judge $ |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in ORDER:
        rs = by.get(e)
        if not rs:
            continue
        j = [r for r in rs if r.get("judge") or r.get("recall")]
        f = sum(1 for r in j if r["recall"] == "found"); p = sum(1 for r in j if r["recall"] == "partial"); m = sum(1 for r in j if r["recall"] == "missed")
        nf = sum(r.get("n_findings", 0) for r in j); nv = sum(r.get("n_valid", 0) for r in j); ni = sum(r.get("n_invalid", 0) for r in j)
        prec = f"{nv / (nv + ni):.0%}" if (nv + ni) else "-"
        print(f"| {e} | {len(rs)} | {len(j)} | {f} | {p} | {m} | {f / len(j):.0%} | {nf / len(j):.1f} | {nv} | {ni} | {prec} | "
              f"{sum(1 for r in rs if r.get('effort_verified'))}/{len(rs)} | {med([r.get('cost_usd') for r in rs])} | {mean([r.get('cost_usd') for r in rs])} | "
              f"{med([(r.get('wall_s') or 0) / 60 for r in rs])} | {mean([(r.get('judge_meta') or {}).get('cost_usd') for r in j])} |" if j else
              f"| {e} | {len(rs)} | 0 | | | | | | | | | {sum(1 for r in rs if r.get('effort_verified'))}/{len(rs)} | {med([r.get('cost_usd') for r in rs])} | {mean([r.get('cost_usd') for r in rs])} | {med([(r.get('wall_s') or 0) / 60 for r in rs])} | |")
    cases = sorted({r["case"] for r in rows}); efforts = [e for e in ORDER if e in by]
    print("\nPer case recall (F=found P=partial M=missed, then findings valid/invalid):\n")
    print("| case | " + " | ".join(efforts) + " |")
    print("|---|" + "---|" * len(efforts))
    for c in cases:
        cells = []
        for e in efforts:
            rs = [r for r in rows if r["case"] == c and r["effort"] == e and (r.get("judge") or r.get("recall"))]
            cells.append(" ".join(f"{r['recall'][0].upper()}{r.get('n_valid', 0)}/{r.get('n_invalid', 0)}" for r in rs) or "-")
        print(f"| {c} | " + " | ".join(cells) + " |")
    print("\nStatus lines:")
    for r in rows:
        print(f"  {r['key']:38s} {str(r.get('status_line'))[:50]:50s} report_from_file={r.get('report_from_file')} {str(r.get('error') or '')[:80]}")


if __name__ == "__main__":
    suite = sys.argv[1]
    rows = rows_for(suite)
    print(f"# {suite}: {len(rows)} rows\n")
    (implement if suite == "implement" else review)(rows)
