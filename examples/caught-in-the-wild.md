# Caught in the wild: the AI building this skill failed at the exact thing it fixes

This is real. It happened during the benchmark run for `ground-first`, unscripted.

## Setup

We were benchmarking the skill. One test prompt:

> "o que você acha do novo modelo que a OpenAI acabou de lançar?"
> ("what do you think of the new model OpenAI just launched?")

The **baseline arm** (web search, no skill) searched and answered accurately: it named real, recent models — **GPT-5.5** (April 2026) and **GPT-5.6 Sol / Terra / Luna** (June 2026) — with official source links.

## The failure

The orchestrating model (Claude, training cutoff August 2025 — *before* those models existed) read that output and confidently declared:

> "B respondeu confiante inventando modelos específicos ('GPT-5.6 Sol/Terra/Luna', '82.7% vs Claude 69.4%') — números que não dá pra verificar e **provavelmente alucinados**."

It dismissed real models as a hallucination — **from memory, without verifying** — because they were past its cutoff.

## The catch

The user, who lives in June 2026:

> "VOCE ACABOU DE FAZER JUSTAMENTE OQUE A SKILL IA CORRIGIR
> GPT-5.6 SOL EXISTE TERRA LUNA TMB PO"

(*"You just did EXACTLY what the skill would have corrected. GPT-5.6 Sol exists, Terra and Luna too, man."*)

## Why this matters

The whole thesis of `ground-first` is: **models confidently fill gaps with stale assumptions and present them as fact.** Here, the model *building the anti-confident-wrongness tool* did it live — about the very topic of recent AI releases — while running the skill's own benchmark.

If grounding had been applied to the orchestrator's own judgment, the rule would have fired: *"recent AI model you can't verify from training → don't assert it's fake, check first."*

You cannot stage a better demonstration that this failure mode is **universal, involuntary, and invisible from the inside.** It isn't a "dumb model" problem. It's a "no model knows what it doesn't know about right now" problem.

That is exactly the gap `ground-first` exists to close.
