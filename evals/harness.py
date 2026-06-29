#!/usr/bin/env python3
"""ground-first - cross-vendor detection harness (one identical HTTP harness).

Runs the GROUND-FIRST PHASE-1 (DETECT) protocol over a labeled query set across many
models from different vendors, all through ONE byte-identical request: an OpenRouter
chat/completions call where only the `model` id changes. This is the cleanest possible
isolation -- the harness is constant, the MODEL is the only variable -- and it directly
refutes "Claude is just grading its own skill": if OpenAI, Google, xAI, Z.ai and
DeepSeek reach the same trigger decisions as Anthropic, the protocol generalizes.

Reproduce:
  set OPENROUTER_API_KEY, then:
  python harness.py cases.json --runs 3 --out detection_results.json

Ground truth is OBJECTIVE (see RUBRIC.md): trigger=yes iff the query references a
post-cutoff entity/event, documented slang/trend, time-dependent niche state, a costly
intent ambiguity, or answer-changing missing context; trigger=no for canonical-stable
queries. Labels are verifiable query properties, not LLM opinion.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

KEY = os.environ.get("OPEN_ROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY", "")
URL = "https://openrouter.ai/api/v1/chat/completions"

# One identical harness; only the model id (and thus the vendor) changes.
MODELS = [
    {"label": "claude-sonnet-4.6", "vendor": "Anthropic", "model": "anthropic/claude-sonnet-4.6"},
    {"label": "gpt-5.5",           "vendor": "OpenAI",    "model": "openai/gpt-5.5"},
    {"label": "gemini-3.1-pro",    "vendor": "Google",    "model": "google/gemini-3.1-pro-preview"},
    {"label": "grok-4.3",          "vendor": "xAI",       "model": "x-ai/grok-4.3"},
    {"label": "glm-5.2",           "vendor": "Z.ai",      "model": "z-ai/glm-5.2"},
    {"label": "deepseek-v4-flash", "vendor": "DeepSeek",  "model": "deepseek/deepseek-v4-flash"},
]

PROMPT = '''You are a CLASSIFIER applying the GROUND-FIRST protocol, PHASE 1 (DETECT) only.
Do NOT answer or solve the user query. Do NOT search. Only classify.

Context-risk signals: platform trends, viral/slang, named cultural phenomena, niche jargon, recent/post-cutoff events, ambiguous proper nouns, implicit pop-culture refs, ambiguous intent.
- LOW    = common, stable, well-documented -> do NOT ground (trigger=no)
- MEDIUM = culturally specific or possibly trending -> ground (trigger=yes)
- HIGH   = clearly trend/slang/viral/niche/recent -> ground (trigger=yes)

USER QUERY:
{query}

Output ONLY this JSON on one line, nothing else: {{"risk":"LOW|MEDIUM|HIGH","trigger":"yes|no"}}'''

JSON_RE = re.compile(r'\{[^{}]*"risk"[^{}]*\}')


def parse(out: str):
    m = JSON_RE.search(out or "")
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except Exception:
        return None
    risk = str(obj.get("risk", "")).upper()
    trig = str(obj.get("trigger", "")).lower()
    if risk not in ("LOW", "MEDIUM", "HIGH") or trig not in ("yes", "no"):
        return None
    return {"risk": risk, "trigger": trig}


def call(model_id, query, timeout=90, attempts=3):
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": PROMPT.format(query=query)}],
        "temperature": 0,
        # generous budget: reasoning models (gemini, gpt) spend hidden tokens before
        # emitting the tiny JSON; too small a cap truncates them to empty (finish=length).
        "max_tokens": 1500,
    }).encode()
    for _ in range(attempts):
        try:
            req = urllib.request.Request(URL, data=body, method="POST", headers={
                "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read().decode("utf-8", "replace"))
            txt = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            parsed = parse(txt)
            if parsed:
                return parsed
        except Exception:
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", default="detection_results.json")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--models", default="", help="comma list of labels to include (default all)")
    args = ap.parse_args()

    models = MODELS if not args.models else [m for m in MODELS if m["label"] in set(args.models.split(","))]
    cases = json.loads(open(args.cases, encoding="utf-8").read())
    for c in cases:
        c["query"] = c.get("prompt") or c.get("query")
    jobs = [(c, m, run) for c in cases for m in models for run in range(1, args.runs + 1)]
    print(f"{len(cases)} cases x {len(models)} models x {args.runs} runs = {len(jobs)} calls", flush=True)

    results, done = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        fut = {ex.submit(call, m["model"], c["query"], args.timeout): (c, m, run) for (c, m, run) in jobs}
        for f in as_completed(fut):
            c, m, run = fut[f]
            parsed = f.result()
            results.append({
                "case_id": c["id"], "name": c.get("name"), "category": c.get("category"),
                "split": c.get("split"), "expected_trigger": c["expected_trigger"],
                "model": m["label"], "vendor": m["vendor"], "run": run,
                "ok": parsed is not None,
                "trigger": parsed["trigger"] if parsed else None,
                "risk": parsed["risk"] if parsed else None,
            })
            done += 1
            if done % 25 == 0 or not parsed:
                t = parsed["trigger"] if parsed else "MISS"
                print(f"[{done}/{len(jobs)}] {m['label']:<18} {str(c.get('name', c['id'])):<26} -> {t}", flush=True)

    json.dump({"models": [{k: m[k] for k in ("label", "vendor", "model")} for m in models],
               "runs": args.runs, "n_cases": len(cases), "results": results},
              open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    cov = {}
    for r in results:
        cov.setdefault(r["model"], [0, 0])
        cov[r["model"]][1] += 1
        cov[r["model"]][0] += 1 if r["ok"] else 0
    print("\n== coverage (responded/total) ==")
    for k, (a, b) in cov.items():
        print(f"  {k:<18} {a}/{b}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
