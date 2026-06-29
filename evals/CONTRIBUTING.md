# Contributing Test Cases

Anyone can add a test case. You don't need to know Python.

> **Canonical set:** the detection benchmark now runs on [`cases.json`](cases.json) (36
> cases, objective labels defined in [`RUBRIC.md`](RUBRIC.md), each with a `split`
> dev/test and a `rationale` citing the rule). To add a **detection** case, add it there —
> schema: `id`, `name`, `category`, `expected_trigger` (yes/no), `risk_expected`,
> `prompt`, `rationale`, `split`. The `evals.json` format below is the v1 pilot set, kept
> for the quality arm's frozen `key_facts`.

## Why test cases matter

Each test case documents a real failure mode — a situation where the AI confidently answered the wrong question. The more test cases we have, the harder it is for the skill to regress silently.

A good test case comes from a real frustration: "I asked the AI about X and it answered as if I meant Y."

---

## Format

Each test case in `evals.json` looks like this:

```json
{
  "id": 10,
  "name": "short-descriptive-name",
  "category": "cultural | platform_specific | versioning | geographic | slang | stack_context | temporal | niche_community | intent_mismatch | control",
  "risk_expected": "HIGH | MEDIUM | LOW",
  "prompt": "the exact message you'd type to the AI",
  "assertions": {
    "grounding_block_shown": true,
    "web_search_should_trigger": true,
    "key_facts_required": ["fact that must appear in response"],
    "response_must_not_contain": ["wrong assumption the model might make"],
    "false_positive": false
  },
  "notes": "Why this is a good test case. What failure mode it catches."
}
```

### Fields explained

| Field | What it means |
|-------|--------------|
| `category` | What type of context problem this tests |
| `risk_expected` | What the skill should classify this as |
| `grounding_block_shown` | Should the skill show a grounding block? |
| `web_search_should_trigger` | Should it search the web before answering? |
| `key_facts_required` | Strings that must appear in the response |
| `response_must_not_contain` | Wrong assumptions that should NOT appear |
| `false_positive: true` | This is a CONTROL case — skill should NOT trigger |

---

## Categories

| Category | Example |
|----------|---------|
| `cultural` | Viral memes, trends, internet culture |
| `platform_specific` | TikTok formats, Instagram features, Reddit culture |
| `versioning` | Framework versions, library APIs that changed |
| `geographic` | Laws, terms, customs that differ by country |
| `slang` | Colloquial language, regional expressions |
| `stack_context` | Tech stack that wasn't specified |
| `temporal` | Events after training cutoff |
| `niche_community` | Game meta, fandom, hobby jargon |
| `intent_mismatch` | Ambiguous request where a plausible-but-wrong reading exists ("delete the user" → soft or hard delete?) |
| `control` | Clear questions where NO grounding is needed |

---

## How to add a test case (no coding needed)

1. Fork this repo
2. Open `evals/evals.json`
3. Add your test case at the end of the `evals` array
4. Give it the next available `id` number
5. Open a PR with the title: `eval: add [your-case-name]`

That's it. You don't need to run the tests yourself — CI will run them.

---

## What makes a great test case

**Good:** A specific, real situation where the AI got it wrong.
> "I asked about the 'rizz' trend and Claude gave me a generic definition instead of explaining the Andrew Tate/Gen Z 2023 specific usage"

**Bad:** An abstract description of a problem.
> "Test that the AI understands cultural references"

**Good control case:** A clear, stable question where grounding would be annoying overhead.
> "how do I convert a string to int in Python?"

**Bad control case:** Something that's actually ambiguous.
> "how do I use the framework?" (Which framework?)

---

## Reporting a failure

If you found a case where `ground-first` still got it wrong, open an issue with:

1. The exact prompt you used
2. What the model answered
3. What it should have answered
4. The category (see table above)

We'll add it as a test case and fix the skill.

---

## Versioning

When test cases are added or the skill is improved, we bump the `version` field in `evals.json`. Each version has a benchmark score — the goal is for that score to go up over time.
