# Example: "very demure, very mindful" — with vs. without ground-first

This is a **real, unedited comparison**. Same prompt, same model (Claude Sonnet 4.6), one with the skill active and one without. Reproduce it yourself with the prompt below.

## The prompt

> *me ajuda a entender aquela coisa do 'very demure, very mindful' que todo mundo tava falando*
>
> (English: "help me understand that 'very demure, very mindful' thing everyone was talking about")

This is a HIGH-risk query: a viral trend the model only partially saw in training, where a generic answer feels plausible but misses what actually happened.

---

## Side by side

| What matters | ❌ Without skill | ✅ With ground-first |
|--------------|------------------|----------------------|
| Who started it | "a content creator" (vague) | **Jools Lebron** (named) |
| When | "2024" (vague) | **August 2024**, peak 2-3 weeks later |
| Cultural weight | not mentioned | **Dictionary.com Word of the Year 2024** |
| Why it spread | "the internet makes things memes" | **counter-reaction to "brat summer"** + brands/celebs joined |
| Creator's story | not mentioned | trans creator who funded her transition via the viral moment |
| Honesty about source | answered from memory | **showed a grounding block** stating it searched the web |

The baseline isn't *wrong* exactly — it gets the gist. But it's the kind of confident, fluent, generic answer that misses every specific detail that makes the trend actually interesting. The user has to go look it up themselves anyway.

---

## What the skill actually showed first

Before answering, ground-first displayed this:

```
┌─ GROUNDING ───────────────────────────────────────────┐
│ What I think you're talking about:                    │
│ A tendência viral do TikTok que explodiu em agosto    │
│ de 2024, onde a criadora Jools Lebron popularizou     │
│ a frase "very demure, very mindful" como descrição    │
│ de um estilo de vida minimalista e consciente.        │
│                                                       │
│ Context gathered: web search + viral trends           │
│ Confidence: HIGH                                      │
│                                                       │
│ Se não for isso, avisa!                              │
└───────────────────────────────────────────────────────┘
```

The user can confirm or correct the interpretation in five words — *before* the model spends 500 tokens answering the wrong question.

---

## Try it yourself

1. Ask any AI the prompt above **without** the skill — note how generic the answer is.
2. Activate ground-first (`/ground`) and ask again.
3. Compare.

The full raw outputs from this run are reproducible by following [the skill's eval setup](../evals/evals.json) (case `viral-trend-cultural`).
