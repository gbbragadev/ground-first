# ground-first — Benchmark Methodology

> **Status: directional pilot.** n=10 detection cases, 4 quality cases, single model (Claude Sonnet 4.6), one run. These numbers indicate direction, not proof. Scaling up (more cases, more samples, more models) is the obvious next step.

## What we are — and aren't — claiming

A naive benchmark ("with skill vs answer-from-memory") is worthless here, because the with-skill arm searches the web and the baseline doesn't. That measures **search vs no-search**, not the skill. Of course fresh search beats stale training on a trend question — that proves nothing about the protocol.

So we split the claim into two, and isolate each:

### Headline metric — Detection accuracy (no confound)

**Claim:** *ground-first knows when to ground and when to stay out of the way.*

This is pure skill logic — no web search involved, fully reproducible. For each query, the skill classifies risk (LOW / MEDIUM / HIGH) and decides whether to trigger grounding. We check:

- **Sensitivity:** does it trigger on genuinely context-risky queries (trends, slang, recent events, ambiguous intent)?
- **Specificity (the important one):** does it stay silent on clear queries (CSS, math)? A grounding skill that fires on everything is useless overhead.

Scored against expected classifications, across 3 independent runs (to show consistency). This metric is the genuinely novel part and survives any scrutiny.

### Supporting metric — Marginal protocol value (search held constant)

**Claim:** *even when both can search, the structured grounding protocol produces a better answer than naive search.*

Three arms, but the number that matters is **C vs B**:

| Arm | Setup | Isolates |
|-----|-------|----------|
| A | Default model, no instruction | What the user gets today (baseline reality) |
| B | "You may search the web" — no skill | Search without the protocol |
| **C** | **Full ground-first skill (also searches)** | **The protocol itself** |

- **A vs C** = total delivered value (only meaningful if the default doesn't already search).
- **B vs C** = *marginal value of the protocol* — this is the honest, confound-free number.

Judged by a **blind grader**: a separate model sees the two answers without knowing which used the skill, and picks the better one on accuracy, specificity, and usefulness.

## Ground truth handling

A blind LLM grader has the same training-cutoff staleness as the model under test — so it must NOT adjudicate facts from its own memory. We separate:

- **Facts** → checked by frozen `key_facts_required` strings in `evals.json`, established by one web search at authoring time (e.g. demure → must contain "Jools Lebron", "2024"). Objective, scriptable.
- **Quality** → the only thing the LLM grader judges (which answer is better-structured, more honest about uncertainty, more useful). Never facts.

## Scope

We benchmark only the categories the skill currently implements (cultural, platform, temporal, niche, intent-ambiguity, geographic) plus controls. Aspirational categories not yet handled by SKILL.md are excluded — benchmarking them would conflate "skill is bad" with "not built yet."

## Reproduce

1. Detection: run the 10 prompts through the skill's PHASE 1 only, record risk + trigger, compare to expected.
2. Quality: run the 4 search-relevant prompts through arms B and C, blind-grade the pairs.
3. Aggregate → `BENCHMARK.md`.
