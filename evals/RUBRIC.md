# Ground-truth labeling rubric (objective, auditable)

The benchmark's headline metric is **detection**: does a model, running the ground-first
PHASE-1 protocol, correctly decide to **ground (trigger=yes)** or **stay silent
(trigger=no)** for a given query?

For that number to mean anything, the *expected* label cannot be an LLM's opinion —
it must be a **property of the query a human can verify**. This file is that rule set.
Every case in [`cases.json`](cases.json) carries a one-line `rationale` that points to
exactly one rule below. If you disagree with a label, you can check it against the rule;
you don't have to trust the authors.

## Label = `yes` (the model SHOULD ground / confirm before answering)

A query gets `expected_trigger: yes` iff **at least one** of these objectively holds:

1. **Post-cutoff reference.** Names or alludes to an entity, product, release, or event
   whose existence/details are datable to *after* a typical model's training cutoff, or
   that is explicitly framed as new ("just launched", "the new X", "latest"). *Verify:*
   the thing has a known launch/peak date you can look up.
2. **Documented trend / slang / meme.** Uses a term whose *intended* meaning is a
   specific internet/cultural phenomenon with a traceable origin, distinct from the
   word's literal/dictionary sense. *Verify:* the slang/trend has a documented origin
   (KnowYourMeme, news, dictionary-of-slang entry).
3. **Time-dependent niche state.** Asks about something whose correct answer changes on
   a schedule the model can't see — game patch meta, "current" rankings, live versions.
   *Verify:* the domain has versioned/patched/dated state.
4. **Intent ambiguity with a costly wrong branch.** A plausible-but-wrong reading exists
   AND acting on it is destructive or expensive (e.g. "delete the user" = soft vs hard
   delete). *Verify:* you can write two materially different correct answers.
5. **Under-specified context that changes the answer.** The right answer depends on
   stack / locale / audience the user hasn't given, and the generic default would
   mislead. *Verify:* name two contexts that yield different correct answers.

## Label = `no` (the model SHOULD answer directly — control)

A query gets `expected_trigger: no` iff **none** of the above apply AND it is:

- **Canonical & stable** — the answer has been the same for years and is exhaustively
  documented (center a div, derivative of x², capital of France, reverse a string).
- **Self-contained** — no missing context changes the answer; one correct response exists.
- **Known stable slang** — colloquial but with a single, settled, widely-known meaning
  the model reliably knows (e.g. PT-BR "enrolando" = stalling). Grounding here is wasted
  overhead → a *specificity* test (the hard, important half of the benchmark).

## Why controls matter as much as risky cases

A grounding skill that fires on everything is useless. **Specificity** (correctly
staying silent on `no` cases) is the metric that separates a real detector from a
"ground everything" stub. This set is deliberately ~50/50 yes/no so specificity is
measured on a meaningful sample, not 2 cases.

## Splits

Cases are split `dev` / `test`, stratified by category and label. Any policy tuning
(e.g. 3-level vs binary trigger) is decided on **dev only**; reported numbers are
**test (held-out)**. The split is frozen in `cases.json`.
