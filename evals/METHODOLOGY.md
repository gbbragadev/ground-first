# ground-first — Benchmark Methodology

> **v2 — scaled.** 36 detection cases (objective labels, held-out dev/test split), **6
> models from 6 independent vendors through one byte-identical OpenRouter HTTP harness**
> (Anthropic, OpenAI, Google, xAI, Z.ai, DeepSeek), 3 runs each = 648 detection calls;
> plus a blind 3-judge quality panel. This replaces the v1 directional pilot (n=10,
> single model, one run). The design below is built to survive the obvious attacks; the
> numbers live in [`../BENCHMARK.md`](../BENCHMARK.md).
>
> *v1 note (kept for honesty): the first pass was a single-model, single-run pilot and
> said so. v2 executes its own "next steps" — and the headline number came **down**, from
> 100% to a pooled balanced accuracy of 0.75. That's the point: scaling is supposed to
> find the warts.*

## What we benchmark — a PHASE-1 distillation, stated plainly

We score a **~10-line classifier prompt that operationalizes the skill's PHASE-1 (DETECT)
logic** — *is this query context-risky (→ ground) or clear (→ stay silent)?* — not the
full 3-phase `SKILL.md` prose. PHASE 1 is the only phase reproducible without live web
search, so it's the only one we can measure cleanly and identically across six vendors.
The exact prompt is the `PROMPT` constant in [`harness.py`](harness.py). A reader diffing
the two files will see the distillation; we'd rather say it first.

## What we are — and aren't — claiming

A naive benchmark ("with skill vs answer-from-memory") is worthless here, because the
with-skill arm searches the web and the baseline doesn't. That measures **search vs
no-search**, not the skill. So we split the claim in two and isolate each.

### Headline metric — Detection accuracy (no confound)

**Claim:** *ground-first knows when to ground and when to stay out of the way.*

Pure skill logic — no web search, fully reproducible. For each query the classifier
decides whether to trigger grounding. We report:

- **Specificity (the important half):** does it stay silent on clear queries (CSS, math)?
  A grounding skill that fires on everything is useless overhead.
- **Sensitivity:** does it trigger on genuinely context-risky queries (trends, slang,
  recent events)?
- **Balanced accuracy** = (sensitivity + specificity) / 2, per vendor, per split, pooled.

Scored against an objective rubric across 3 independent runs (consistency check).

### Supporting metric — Marginal protocol value (search held constant)

**Claim:** *even when both can search, the structured protocol produces a better answer
than naive search.* Arms: **B** = "you may search the web" (no skill); **C** = full
ground-first (also searches). **B vs C** is the honest, confound-free number. Judged by a
**blind 3-judge panel** (answers shown as A/B in swapped order; judges blind to which used
the skill; facts never judged by the LLM — see below). Kept **Claude-only on purpose**:
cross-vendor quality needs reliable per-vendor web search, which is noisy.

## Ground truth handling

A blind LLM grader has the same training-cutoff staleness as the model under test — so it
must NOT adjudicate facts from its own memory. We separate:

- **Facts** → checked by frozen `key_facts` strings, established by one web search at
  authoring time (e.g. demure → must contain "Jools Lebron", "2024"). Objective, scriptable.
- **Quality** → the only thing the LLM panel judges (better-structured, more honest about
  uncertainty, more useful). Never facts.

## How the scale-up answers the three obvious attacks

**Attack 1: "Claude is just grading its own skill."** The detection harness sends **one
byte-identical OpenRouter `chat/completions` request** and varies *only* the `model` id.
Six genuinely independent vendors go through it — Anthropic (claude-sonnet-4.6), OpenAI
(gpt-5.5), Google (gemini-3.1-pro), xAI (grok-4.3), Z.ai (glm-5.2), DeepSeek
(deepseek-v4-flash). Because the harness is constant, the *model* is the only variable. If
five non-Anthropic vendors reach the same trigger decisions as Claude, the protocol is not
a Claude-shaped artifact. They largely do: **78% of cases are unanimous across all six.**
(Models are reached via OpenRouter, which proxies to each vendor.)

**Attack 2: "The labels are your opinion."** Ground truth is a **published, objective
rubric** ([`RUBRIC.md`](RUBRIC.md)). A query is `trigger=yes` iff it objectively
references a post-cutoff entity/event, documented slang/trend, time-dependent niche state,
a costly intent ambiguity, or answer-changing missing context — each case cites the exact
rule in its `rationale`. A human can audit every label without trusting us. We pool LLM
labelers *nowhere*: with the model family under test, agreement would prove shared
training, not correctness. **And we let the labels lose:** three categories
(`intent_mismatch`, `stack_context`, `geographic`) score near-zero across all six vendors
— see [`../BENCHMARK.md`](../BENCHMARK.md) for the "the labels may be wrong, not the
models" reading, which we surface rather than bury.

**Attack 3: "You only test cases it passes."** The set is deliberately **~50/50** (18
trigger / 18 control). Specificity — staying silent on canonical-stable queries — is half
the cases, so a "ground everything" stub scores 50%, not a free pass. Cases are split
**dev/test**; everything is reported on the held-out **test** split as well as pooled.

### Reporting scope — full first, scoped as a breakdown

The README advertises some of the weak categories (ambiguous intent, regional context),
so the **headline is the full number** (pooled balanced accuracy **0.75**, sensitivity
0.52, specificity 0.98) with the full per-category table. We also report a **scoped** view
(balanced accuracy **0.905**, test **0.875**) over the categories the search-grounding
protocol actually targets — clearly labeled as a breakdown, never the top line.
Cherry-picking the scoped number as the headline would be exactly the dishonesty this
methodology exists to prevent.

### The "weights" question — and why we don't dress it up

The pilot asked whether the 3-level risk scale (LOW/MEDIUM/HIGH) beats a binary trigger.
We can't honestly answer it: the classifier prompt **states the mapping** (`LOW→no`,
`MEDIUM/HIGH→yes`), so DIRECT (the binary trigger) and RISK3 (trigger derived from the
3-level label) collapse to one **by construction** — 0/648 divergence. That's the model
echoing an instruction we gave it, not a result. A real test would withhold the mapping
and let the model choose; we list it as future work instead of inventing a finding.

### Quality arm (supporting, single-vendor on purpose)

The marginal-value arm (B = search no skill, C = skill) needs reliable per-vendor web
search, noisy cross-vendor — so it stays **Claude-only**, with a **blind 3-judge panel**
(answers as A/B in swapped order; frozen `key_facts` checked in-script, never by the
judge). Supporting evidence, not the headline.

## Reproduce

```bash
export OPENROUTER_API_KEY=...   # one key, all six vendors
# Detection (6 vendors through the identical HTTP harness):
python evals/harness.py  evals/cases.json --runs 3 --out evals/detection_results.json
# Metrics (per-vendor, per-split, per-category, cross-vendor agreement, scoped):
python evals/analyze.py  evals/detection_results.json evals/metrics.json
```

The labeled set ([`cases.json`](cases.json)), the rubric ([`RUBRIC.md`](RUBRIC.md)), the
harness, and the analyzer are all in this folder; every number in
[`../BENCHMARK.md`](../BENCHMARK.md) regenerates from them.
