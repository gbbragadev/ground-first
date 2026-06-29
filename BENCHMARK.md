# ground-first — Benchmark

> **v2 — scaled, and the numbers came down. That's the point.** The v1 pilot (n=10,
> one model, one run) reported 100% sensitivity / 100% specificity. Scaling to **36
> labeled cases × 6 models from 6 independent vendors × 3 runs (648 detection calls)**
> revises that to a **pooled balanced accuracy of 0.75** — specificity stays near-perfect,
> sensitivity splits hard by category. This is the honest version the flattering pilot
> couldn't be. A benchmark that only flatters the tool is marketing; the first skeptic
> breaks it. Full design in [`evals/METHODOLOGY.md`](evals/METHODOLOGY.md).

### What is actually being tested (read this first)

This benchmark measures a **~10-line classifier distillation of the skill's PHASE-1
(DETECT) logic** — *"is this query context-risky → ground, or clear → stay silent?"* —
not the full 3-phase `SKILL.md` prose. PHASE 1 is the only phase reproducible without
live web search, so it's the only one measurable cleanly across vendors. The exact
prompt is in [`evals/harness.py`](evals/harness.py).

---

## Headline — Detection across 6 vendors, one identical harness

Every model is called through the **exact same** OpenRouter HTTP request; only the
`model` id changes. The *model* is the only variable — the direct answer to "Claude is
just grading its own skill." Six vendors, 108 calls each, 100% response coverage:

| Vendor | Model | Specificity | Sensitivity | Balanced acc |
|---|---|---|---|---|
| OpenAI | gpt-5.5 | 1.00 | 0.65 | **0.824** |
| Google | gemini-3.1-pro | 1.00 | 0.61 | **0.806** |
| Anthropic | claude-sonnet-4.6 | 0.94 | 0.61 | **0.778** |
| xAI | grok-4.3 | 0.96 | 0.52 | **0.741** |
| Z.ai | glm-5.2 | 1.00 | 0.43 | **0.713** |
| DeepSeek | deepseek-v4-flash | 0.98 | 0.31 | **0.648** |

**Pooled (all 6 vendors, held-out test split): specificity 1.00, sensitivity 0.50,
balanced accuracy 0.75.** (Dev/all are within ±0.01 — see [`evals/metrics.json`](evals/metrics.json).)

Two things are true at once and both matter:

1. **Specificity is excellent and universal (0.94–1.00).** Every vendor reliably stays
   silent on clear, canonical queries (CSS, math, capital cities). A grounding skill
   that fires on everything is useless overhead — this one does not. *This is the
   strongest, cleanest result and it holds across every vendor.*
2. **Sensitivity is mediocre and uneven (0.31–0.65).** Models miss many "risky" queries.
   But the misses aren't random — they concentrate almost entirely in three categories.

## Where it works and where it doesn't — the per-category table

Accuracy pooled across all 6 vendors (control rows = specificity; the rest = sensitivity):

| Category | Cases | Accuracy | |
|---|---|---|---|
| control (CSS, math, facts) | 18 | **0.98** | ✅ stays silent |
| cultural (demure, viral sound) | 2 | **1.00** | ✅ |
| slang (brain rot, mewing, looksmaxxing) | 3 | **0.98** | ✅ |
| niche_community (game meta) | 1 | **0.83** | ✅ |
| temporal (just-launched model, new iPhone) | 2 | **0.78** | ✅ |
| platform_specific (TikTok POV format) | 1 | **0.72** | 🟡 |
| versioning (new Angular/Next router) | 2 | **0.53** | 🟡 split |
| **geographic** (BR labor law) | 1 | **0.11** | ❌ |
| **stack_context** (auth for "my API", pricing) | 3 | **0.06** | ❌ |
| **intent_mismatch** ("delete the user") | 3 | **0.00** | ❌ |

On the categories the skill is really built for — trends, slang, recency, niche,
controls — it does well across vendors (the *scoped* view below). The three ❌ categories
drag the pooled number to 0.75, and they deserve an honest read.

## The most interesting finding: the skill bundles two different actions

When **all six independent vendors** agree — `intent_mismatch` triggers **0/54 times**,
`stack_context` **3/54 (6%)** — the parsimonious explanation is *not* "six models are
all wrong." It's that **these aren't web-search-grounding cases.**

"Delete the user" doesn't need a *web search* — it needs a *clarifying question*
(soft-delete or hard-delete?). "Auth for my API" needs to know your stack, not a search.
The skill's GROUND action is literally *"search the web,"* but these categories call for
a different action: **ask before acting.** The benchmark surfaced that `ground-first`
quietly bundles **two distinct behaviors** — *search-before-answering* and
*clarify-before-acting* — and **only the search-grounding one generalizes across models.**

Two honest readings, and we don't pick one for you:
- **(a) Skill gap / roadmap.** The DETECT logic doesn't reliably fire on intent/stack
  ambiguity. `intent_mismatch` was already the pilot's known-unimplemented category; this
  quantifies it across 6 vendors.
- **(b) The labels conflate two actions.** Six-vendor unanimity is decent evidence that
  the *label* ("these should trigger web-grounding") is what's off — they should trigger
  a clarifying question, a behavior this benchmark doesn't measure.

Either way it's a concrete, credible thing the scaled benchmark told us that the pilot couldn't.

## Scoped view — on the categories it's built for

Excluding the three ❌ categories (objective context-risk only: cultural, slang, temporal,
niche, platform, versioning + controls) — **a breakdown, not the headline**, because the
README advertises some of the excluded behaviors:

| | sensitivity | specificity | balanced acc |
|---|---|---|---|
| all splits | 0.83 | 0.98 | **0.905** |
| **held-out test** | 0.75 | 1.00 | **0.875** |

Per-vendor on this scope: gpt-5.5 **1.00**, gemini-3.1-pro **1.00**, claude-sonnet-4.6
0.93, grok-4.3 0.91, glm-5.2 0.85, deepseek-v4-flash 0.75. The protocol's
*search-grounding* behavior generalizes well across every vendor tested.

## Cross-vendor agreement & stability

- **Unanimous trigger decision across all 6 vendors on 28/36 cases (78%).** The 8
  disagreements are exactly the borderline cases — versioning, intent, stack, one niche,
  one temporal — i.e. vendors agree on the clear-cut queries and split only where the
  call is genuinely debatable. That's the agreement pattern you'd want.
- **96% run-to-run consistency** (208/216 case×model cells identical across 3 runs): the
  decision is stable, not coin-flippy.

## A note on the "weights" / policy question

The pilot wondered whether the 3-level risk scale (LOW/MEDIUM/HIGH) beats a binary
trigger. We can't honestly answer it here: the classifier prompt **states the mapping**
(`LOW→no`, `MEDIUM/HIGH→yes`), so the two collapse to one by construction (0/648
divergence) — that's the prompt echoing an instruction, not a result. A real test would
withhold the mapping and let the model choose. Future work, reported as such rather than
dressed up as a finding.

---

## Supporting: marginal protocol value (blind 3-judge panel)

Detection is the headline. The softer claim — *does the protocol produce a better answer
when both arms can search?* — is tested with a **blind 3-judge panel** (judges see the
two answers as A/B in swapped order, blind to which used the skill; frozen `key_facts`
checked in-script, never by the judge). Kept **single-vendor (Claude)** on purpose:
cross-vendor quality needs reliable per-vendor web search, which is noisy. 5
search-relevant cases, arms **B** (search, no skill) vs **C** (skill). Data:
[`evals/quality_panel.json`](evals/quality_panel.json).

**Result: a marginal, honest win.** The skill takes the majority of head-to-heads
(**3/5**), and more importantly:

- **Calibrated honesty:** judged *more honest about uncertainty* in **4/5** cases.
- **Frozen facts:** matched or beat the baseline on key-fact coverage in **every**
  fact-checkable case (e.g. labor-rights 2/2 vs 1/2; demure 2/2 vs 1/2).
- **Its one clear loss** (`openai-new`) is **over-caution** — it paused to clarify when
  search already had the answer. The same failure the pilot found, reproduced blind.

The protocol's real value is *calibrated honesty + correctability*, not raw answer quality.

## Exhibit A: the failure mode, caught live

During the *v1* benchmark, the orchestrating model (Claude) read a correct answer naming
real, recent OpenAI models and confidently dismissed them as *"probably hallucinated"* —
the exact confident-wrongness the skill exists to prevent, performed live by the model
building it. Full writeup: [`examples/caught-in-the-wild.md`](examples/caught-in-the-wild.md).

## Limitations (honest)

- **We test a PHASE-1 distillation**, not the full prose skill. The DETECT decision is the
  measurable core; the GROUND/ANSWER phases need live search and aren't scored here.
- **Label contestability.** The three ❌ categories may be mislabeled (see "two readings")
  rather than skill failures — 6-vendor unanimity is evidence the labels conflate
  search-grounding with clarify-before-acting.
- **Quality arm is single-vendor and small** (5 cases, Claude) — directional.
- **Scale is modest** (36 cases). Enough to separate strong categories from weak ones and
  to show cross-vendor generalization; not enough for fine claims within a category.
- **Models reached via OpenRouter**, which proxies to each vendor.

## Reproduce

```bash
export OPENROUTER_API_KEY=...   # one key, all six vendors
python evals/harness.py  evals/cases.json --runs 3 --out evals/detection_results.json
python evals/analyze.py  evals/detection_results.json evals/metrics.json
```

The labeled set ([`evals/cases.json`](evals/cases.json), 36 cases, objective rubric in
[`evals/RUBRIC.md`](evals/RUBRIC.md), frozen dev/test split), the harness, and the
analyzer are all in [`evals/`](evals/). Every number above regenerates from them.
