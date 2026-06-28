# ground-first — Benchmark

> **Status: directional pilot.** 10 detection cases, 4 quality cases, single model (Claude Sonnet 4.6), one run, 2026-06-28. These numbers show *direction*, not proof. They are deliberately reported with their warts — a benchmark that only flatters the tool is marketing, and the first skeptic breaks it. See [Limitations](#limitations).

Full design in [`evals/METHODOLOGY.md`](evals/METHODOLOGY.md). The short version: a naive "skill vs answer-from-memory" comparison is worthless here, because it measures *web search vs no search*, not the skill. So we split the claim in two and isolate each.

---

## Headline: Detection accuracy (no confound, reproducible)

**Claim: ground-first knows when to ground — and when to stay out of the way.**

This is pure skill logic, no web search involved. For each query the skill classifies risk and decides whether to trigger grounding. Run 3× independently to show consistency.

| Metric | Result |
|--------|--------|
| **Specificity** — controls (CSS, math) correctly left alone | **6/6 = 100%** across all 3 runs |
| **Sensitivity** — in-scope risky queries correctly grounded | **21/21 = 100%** across all 3 runs |
| Overall trigger accuracy | Run1 10/10, Run2 9/10, Run3 9/10 → **mean 93.3%** |
| Single miss | `delete user` (intent ambiguity) triggered 1/3 — a category SKILL.md doesn't implement yet → roadmap, not a hidden defect |

**The number that matters most is the 100% specificity.** A grounding skill that fires on everything is useless overhead; this one stays silent on clear technical/math queries every time, while catching every trend/slang/recent-event query it's built to catch.

*Secondary note:* the risk **level** (HIGH↔MEDIUM) wobbled across runs on a few cases, but the **trigger decision** (ground or don't) stayed constant. The operationally meaningful output is robust even when the label isn't — a hint that a binary trigger/no-trigger scale may be cleaner than three levels.

---

## Supporting: Marginal protocol value (search held constant)

**Claim under test: even when both arms can search, the protocol produces a better answer.**

Three arms; the honest number is **C vs B** (both can search — isolates the protocol from search):
- **B** = web search allowed, no skill
- **C** = full ground-first skill (also searches)

### Result: mixed. This is the honest part.

| Case | B (search, no skill) | C (skill) | Honest verdict |
|------|----------------------|-----------|----------------|
| **demure** | Search worked → named Jools Lebron, Aug 2024 ✓ | Search **blocked** this run → confessed it couldn't trace origin, described the pattern, told user how to find it | **B better on facts** — but purely search-luck. C's win: it **didn't hallucinate** when it couldn't verify |
| **POV ironic** | Solid generic ironic-POV guide | Grounding block + comparable guide | **Tie.** C adds an explicit interpretation-check |
| **OpenAI new model** | Searched → named real GPT-5.5 / GPT-5.6 Sol·Terra·Luna with sources ✓ | Paused: "which model — the delay or the launch?" | **B better.** C was **over-cautious** — the search had the answer; asking cost value |
| **ADC ranked meta** | Searched → current patch 26.13 meta | Searched → same patch 26.13 meta + grounding block | **Tie.** C marginally more transparent |

**Conclusion: ground-first does NOT reliably produce "better answers" when both arms can search.** Claiming otherwise would be dishonest. What the protocol actually buys is narrower and realer:

1. **Calibrated honesty.** Across all 4 cases C never asserted a false fact. When it couldn't verify (demure, search blocked) it said so; when the query was ambiguous (OpenAI) it asked. It is **never confidently wrong** — which is the entire thesis. The cost: that caution sometimes under-delivers (the OpenAI case).
2. **Correctability.** The grounding block lets you catch a wrong interpretation in five words before the model spends 500 tokens on it. An accuracy benchmark structurally **cannot** measure this — but it's the day-to-day value.

---

## Exhibit A: the failure mode, caught live

During this very benchmark, the orchestrating model (Claude, training cutoff Aug 2025) read arm-B's correct answer naming **GPT-5.6 Sol / Terra / Luna** and confidently declared them *"probably hallucinated"* — dismissing real, recent models from memory, without verifying. The user (who lives in June 2026) caught it: *"you just did EXACTLY what the skill corrects."*

Full writeup: [`examples/caught-in-the-wild.md`](examples/caught-in-the-wild.md).

You cannot stage a better demonstration that this failure mode is **universal, involuntary, and invisible from the inside** — the model *building the anti-confident-wrongness tool* did it live, about recent AI releases, mid-benchmark. That's the strongest qualitative evidence in this whole document, and it wasn't planned.

---

## What this pilot actually establishes

- **Strong:** the skill reliably distinguishes "needs grounding" from "leave it alone," with zero false-positive overhead on clear queries. (Detection.)
- **Real but narrow:** the protocol's value when searching is *calibrated honesty + correctability*, not raw answer quality.
- **Honest limitation:** the "pause to clarify" behavior can be over-cautious on answerable queries (OpenAI case). Worth tuning.
- **Qualitative:** the problem the skill targets is real enough that the model building it fell into the trap unprompted.

## Limitations

- n=10 detection / 4 quality, **single run, single model.** Directional, not proven.
- Web-search availability was **inconsistent** across agent runs (demure-C was blocked while demure-B searched fine). This noise dominates the fact-level quality outcome and is exactly why detection (search-free) is the headline.
- Quality grading here is the authors' open analysis, not a blind panel. A blind multi-judge pass is the obvious next step.

## Next steps

- Scale to 30–50 cases, 3+ samples/arm, 2–3 models (Claude / GPT / Gemini).
- Add a blind multi-judge quality panel.
- Implement + benchmark the `intent_mismatch` category (the one detection miss).
- Tune the over-caution: when search yields a confident answer, prefer answering with a one-line caveat over pausing.

## Reproduce

1. Detection: run the 10 prompts through PHASE 1 only, record risk + trigger, compare to expected. See [`evals/evals.json`](evals/evals.json).
2. Quality: run the 4 search-relevant prompts through arms B and C, compare.
