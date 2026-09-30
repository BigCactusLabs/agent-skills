#!/usr/bin/env python3
"""Summarize results/codex-implement.jsonl by (model, effort) arm. Recomputes every headline from raw rows.
Cost is list price from token usage (output_tokens taken to include reasoning); credits per the Codex rate card."""
import json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rows_for(path=None):
    f = Path(path) if path else ROOT / "results" / "codex-implement.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


def report(rows):
    arms = sorted({(r["model"], r["effort"]) for r in rows})
    print("| arm | n | pass | errors | verified | mean $ | mean credits | median wall | median cmds | mean out tok | mean in tok (cached) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for m, e in arms:
        rs = [r for r in rows if r["model"] == m and r["effort"] == e]
        walls = [r["wall_s"] for r in rs if r.get("wall_s")]
        cmds = [r["commands"] for r in rs if r.get("commands") is not None]
        us = [r["usage"] for r in rs if r.get("usage")]
        costs = [r["cost_usd"] for r in rs if r.get("cost_usd") is not None]
        crs = [r["credits"] for r in rs if r.get("credits") is not None]
        if not costs:
            print(f"| {m} {e} | {len(rs)} | - | {sum(1 for r in rs if r.get('is_error'))} | - | - | - | - | - | - | - |"); continue
        print(f"| {m} {e} | {len(rs)} | {sum(1 for r in rs if r.get('pass'))} | {sum(1 for r in rs if r.get('is_error'))} | "
              f"{sum(1 for r in rs if r.get('effort_verified'))} | ${sum(costs)/len(costs):.2f} | {sum(crs)/len(crs):.1f} | "
              f"{st.median(walls)/60:.1f} min | {st.median(cmds) if cmds else '-'} | "
              f"{int(sum(u.get('output_tokens',0) for u in us)/len(us))} | "
              f"{int(sum(u.get('input_tokens',0) for u in us)/len(us)/1000)}K ({int(sum(u.get('cached_input_tokens',0) for u in us)/len(us)/1000)}K) |")
    passes = {(m, e): sum(1 for r in rows if r["model"] == m and r["effort"] == e and r.get("pass")) for m, e in arms}
    for m, e in arms:
        rs = [r for r in rows if r["model"] == m and r["effort"] == e and r.get("cost_usd") is not None]
        if rs and passes[(m, e)]:
            print(f"cost per success {m} {e}: ${sum(r['cost_usd'] for r in rs)/passes[(m, e)]:.2f}  "
                  f"({sum(r['credits'] for r in rs)/passes[(m, e)]:.1f} credits)")
    cases = sorted({r["case"] for r in rows})
    print("\n| case | " + " | ".join(f"{m} {e}" for m, e in arms) + " |")
    print("|---|" + "---|" * len(arms))
    for c in cases:
        cells = []
        for m, e in arms:
            rs = [r for r in rows if r["case"] == c and r["model"] == m and r["effort"] == e]
            cells.append(" ".join(("P" if r.get("pass") else ("E" if r.get("is_error") else "F"))
                                  + f" ${r.get('cost_usd') or 0:.2f} {int((r.get('wall_s') or 0)/60)}m" for r in rs) or "-")
        print(f"| {c} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    report(rows_for(sys.argv[1] if len(sys.argv) > 1 else None))
