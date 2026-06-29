#!/usr/bin/env python3
"""Analyze detection_results.json -> metrics.json + readable tables.

Metrics (binary trigger decision: ground=yes vs stay-silent=no):
  sensitivity  = correctly grounded among expected-yes  (TP rate)
  specificity  = correctly silent among expected-no      (TN rate)  <- the hard half
  balanced_acc = (sensitivity + specificity) / 2

Reported per model/vendor, per split, per category, plus cross-vendor agreement and
cross-run consistency. The "weights" question (discrete policy) is tested last:
DIRECT (model's binary trigger) vs RISK3 (derive trigger from the 3-level risk label),
chosen on dev, reported on held-out test.
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict

PATH = sys.argv[1] if len(sys.argv) > 1 else "detection_results.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "metrics.json"
data = json.load(open(PATH, encoding="utf-8"))
R = [r for r in data["results"] if r["ok"]]  # only parsed responses


def metrics(rows, trig_key="trigger"):
    tp = fp = tn = fn = 0
    for r in rows:
        exp = r["expected_trigger"]
        got = r[trig_key] if trig_key in r else r["trigger"]
        if exp == "yes":
            if got == "yes": tp += 1
            else: fn += 1
        else:
            if got == "no": tn += 1
            else: fp += 1
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    n = tp + fp + tn + fn
    acc = (tp + tn) / n if n else float("nan")
    bal = (sens + spec) / 2 if (tp + fn) and (tn + fp) else float("nan")
    return {"n": n, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "sensitivity": round(sens, 4), "specificity": round(spec, 4),
            "accuracy": round(acc, 4), "balanced_acc": round(bal, 4)}


def risk3(rows):
    # derive trigger from 3-level risk: HIGH/MEDIUM -> yes, LOW -> no
    out = []
    for r in rows:
        rr = dict(r)
        rr["trig_risk3"] = "yes" if r.get("risk") in ("HIGH", "MEDIUM") else "no"
        out.append(rr)
    return out


report = {"source": PATH, "n_responses": len(R), "models": data["models"]}

# per-model overall
print("== per model (all splits) ==")
print(f"{'model':<18}{'vendor':<11}{'cov':>7}  sens  spec  bal_acc")
report["per_model"] = {}
total_jobs = defaultdict(int)
for r in data["results"]:
    total_jobs[r["model"]] += 1
for m in data["models"]:
    lab = m["label"]
    rows = [r for r in R if r["model"] == lab]
    mm = metrics(rows)
    cov = f"{len(rows)}/{total_jobs[lab]}"
    report["per_model"][lab] = {"vendor": m["vendor"], "coverage": cov, **mm}
    print(f"{lab:<18}{m['vendor']:<11}{cov:>7}  {mm['sensitivity']:.2f}  {mm['specificity']:.2f}  {mm['balanced_acc']:.3f}")

# per split per model
report["per_split"] = {}
for split in ("dev", "test"):
    report["per_split"][split] = {}
    print(f"\n== split={split} ==")
    print(f"{'model':<18}  sens  spec  bal_acc")
    for m in data["models"]:
        lab = m["label"]
        rows = [r for r in R if r["model"] == lab and r["split"] == split]
        mm = metrics(rows)
        report["per_split"][split][lab] = mm
        print(f"{lab:<18}  {mm['sensitivity']:.2f}  {mm['specificity']:.2f}  {mm['balanced_acc']:.3f}")

# pooled across all models (the cross-vendor headline)
print("\n== pooled across ALL models ==")
for split in ("dev", "test", None):
    rows = [r for r in R if (split is None or r["split"] == split)]
    mm = metrics(rows)
    key = split or "all"
    report.setdefault("pooled", {})[key] = mm
    print(f"  {key:<5} sens {mm['sensitivity']:.3f}  spec {mm['specificity']:.3f}  bal {mm['balanced_acc']:.3f}  (n={mm['n']})")

# per category (pooled)
print("\n== per category (pooled, all models) ==")
cats = sorted(set(r["category"] for r in R))
report["per_category"] = {}
for c in cats:
    rows = [r for r in R if r["category"] == c]
    mm = metrics(rows)
    report["per_category"][c] = mm
    print(f"  {c:<18} bal {mm['balanced_acc'] if mm['balanced_acc']==mm['balanced_acc'] else float('nan'):.3f}  acc {mm['accuracy']:.3f}  (n={mm['n']})")

# cross-vendor agreement per case (majority trigger per model, then do vendors agree?)
print("\n== cross-vendor agreement (per case, majority vote per model) ==")
by_case = defaultdict(lambda: defaultdict(list))
for r in R:
    by_case[r["case_id"]][r["model"]].append(r["trigger"])
agree = 0; total = 0; disagreements = []
for cid, perm in by_case.items():
    votes = {}
    for mdl, ts in perm.items():
        votes[mdl] = "yes" if ts.count("yes") >= ts.count("no") else "no"
    vals = set(votes.values())
    total += 1
    if len(vals) == 1:
        agree += 1
    else:
        disagreements.append({"case_id": cid, "votes": votes})
report["cross_vendor_agreement"] = {"unanimous": agree, "total": total,
                                    "rate": round(agree / total, 4) if total else None,
                                    "disagreements": disagreements}
print(f"  unanimous trigger decision across all models: {agree}/{total} ({100*agree/total:.0f}%)")
for d in disagreements:
    print(f"    case {d['case_id']}: {d['votes']}")

# cross-run consistency: per (case,model), do the runs agree?
stable = 0; tot = 0
for cid, perm in by_case.items():
    for mdl, ts in perm.items():
        tot += 1
        if len(set(ts)) == 1:
            stable += 1
report["cross_run_consistency"] = {"stable": stable, "total": tot,
                                   "rate": round(stable / tot, 4) if tot else None}
print(f"\n== cross-run consistency: {stable}/{tot} (case,model) cells identical across runs ({100*stable/tot:.0f}%) ==")

# "weights" / policy: DIRECT vs RISK3, dev -> test
print("\n== policy (pesos): DIRECT binary trigger vs RISK3 (3-level->binary) ==")
R3 = risk3(R)
report["policy"] = {}
for split in ("dev", "test"):
    rows = [r for r in R3 if r["split"] == split]
    direct = metrics(rows, "trigger")
    r3 = metrics(rows, "trig_risk3")
    report["policy"][split] = {"DIRECT": direct, "RISK3": r3}
    print(f"  {split}: DIRECT bal={direct['balanced_acc']:.3f}  RISK3 bal={r3['balanced_acc']:.3f}")
# how often direct trigger disagrees with risk-derived (label wobble vs decision)
disagree = sum(1 for r in R3 if r["trigger"] != r["trig_risk3"])
report["policy"]["direct_vs_risk3_disagree"] = {"n": disagree, "of": len(R3),
    "rate": round(disagree / len(R3), 4) if R3 else None}
print(f"  DIRECT vs RISK3 disagree on {disagree}/{len(R3)} responses ({100*disagree/len(R3):.1f}%)")

# scoped: objective categories only (exclude the soft/known-unimplemented ones)
SOFT = {"intent_mismatch", "stack_context", "geographic"}
report["scoped"] = {"excluded_categories": sorted(SOFT)}
print("\n== SCOPED (objective categories only; soft/unimplemented excluded) ==")
for split in ("dev", "test", None):
    rows = [r for r in R if r["category"] not in SOFT and (split is None or r["split"] == split)]
    mm = metrics(rows)
    report["scoped"][split or "all"] = mm
    print(f"  {split or 'all':<5} sens {mm['sensitivity']:.3f}  spec {mm['specificity']:.3f}  bal {mm['balanced_acc']:.3f}")
report["scoped"]["per_model"] = {}
for m in data["models"]:
    rows = [r for r in R if r["model"] == m["label"] and r["category"] not in SOFT]
    report["scoped"]["per_model"][m["label"]] = metrics(rows)
report["soft_category_trigger_rate"] = {}
for c in sorted(SOFT):
    rows = [r for r in R if r["category"] == c]
    fired = sum(1 for r in rows if r["trigger"] == "yes")
    report["soft_category_trigger_rate"][c] = {"fired": fired, "of": len(rows),
                                               "rate": round(fired / len(rows), 4) if rows else None}

json.dump(report, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\nwrote {OUT}")
