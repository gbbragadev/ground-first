# ground-first

> A portable AI skill that forces any model to understand what you're actually talking about before responding.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Works with Claude Code](https://img.shields.io/badge/Claude%20Code-/ground-blue)](https://claude.ai/code)
[![Works with Codex](https://img.shields.io/badge/Codex-%24ground-green)](https://openai.com/codex)

---

## Who is this for?

**If you've ever felt like the AI "doesn't get it"** — you explained your idea with your own words, referenced something from your world, and the AI answered as if you were someone completely different — this is for you.

You might be:
- A **creator** building content around a trend and the AI gives you generic advice instead of understanding what's actually happening in that niche
- An **indie builder** describing your app idea in your own language and the AI assumes a completely different use case
- A **solopreneur** asking about something specific to your community, your market, your culture — and the AI answers for a generic global audience instead
- A **developer** getting burned by the model assuming the wrong framework version or tech stack

The common thread: **the AI answered confidently to a question you didn't ask.**

---

## The Problem

You say: *"help me with that TikTok thing with parkour background"*

The model hears: *"parkour videos on TikTok"*

You meant: *a specific viral audio trend from 2024 where creators use high-energy parkour music for transitions.*

LLMs interpret prompts using training-data patterns — the **most common** meaning of words, not the **specific** meaning you have in mind. This gap is widest for:

- Trending content and viral memes
- Platform-specific formats (TikTok, Instagram, Reddit culture)
- Regional slang and colloquialisms
- Niche community references
- Anything that happened after the model's training cutoff
- Your personal/professional context that the model simply doesn't know

The result: confident, fluent, **wrong** responses — and wasted time correcting them.

---

## Quick start — no coding needed

If you just want to try it, copy this line and paste it at the beginning of any chat:

```
Before answering, tell me what you think I'm talking about. If it involves trends, slang, platform culture, or anything time-sensitive, search the web first. Show me your interpretation before giving the full answer.
```

For a more complete and configurable version, see [Installation](#installation) below.

---

## The Solution

`ground-first` forces a mandatory 3-phase protocol before any response:

```
PHASE 1 — DETECT     Scan for context-risk signals (trends, slang, viral content, niche refs)
PHASE 2 — GROUND     Search the web if needed, then show explicit interpretation block
PHASE 3 — ANSWER     Respond with verified context
```

**Before answering, the model shows:**

```
┌─ GROUNDING ───────────────────────────────────────────┐
│ What I think you're talking about:                    │
│ The "very demure, very mindful" viral trend started   │
│ by TikTok creator Jools Lebron in August 2024...      │
│                                                       │
│ Context gathered: web search (Reddit + news)          │
│ Confidence: HIGH                                      │
│                                                       │
│ If this is wrong, say so before I continue.          │
└───────────────────────────────────────────────────────┘
```

You can correct a wrong interpretation in 5 words. You can't un-read a 500-word response built on the wrong premise.

---

## Benchmark

Full results — including the warts — in [**BENCHMARK.md**](BENCHMARK.md). Directional pilot, honestly reported.

**Headline (reproducible, no confound):** across 3 runs, the skill correctly grounded **21/21** in-scope risky queries and correctly left **6/6** control queries (CSS, math) alone — **100% specificity, zero false-positive overhead.** It knows when to act *and* when to stay out of the way.

**Honest caveat:** when both the skill and a plain search-enabled baseline can search the web, the skill does **not** reliably produce better answers. What it buys is *calibrated honesty* (it's never confidently wrong) and *correctability* (you catch a bad interpretation before the full answer) — not raw answer quality. We say so plainly in the benchmark, because a benchmark that only flatters the tool is marketing.

**Exhibit A — caught live:** mid-benchmark, the model *building this skill* confidently dismissed real, recent AI models as "hallucinated" — the exact failure ground-first exists to fix. See [`examples/caught-in-the-wild.md`](examples/caught-in-the-wild.md). You can't stage a better proof that this problem is universal and invisible from the inside.

---

## Token Economy

The question isn't *"how many tokens does grounding cost?"* — it's *"how many tokens does a wrong response cost?"*

| Scenario | Tokens |
|----------|--------|
| Wrong response + correction + rewrite | 600–1,600 |
| `ground-first` overhead (lite mode) | 10–20 |

**Ground-first pays for itself after 1 avoided misinterpretation.**

---

## Installation

### Claude Code

```bash
# Method 1: Copy SKILL.md to your skills directory
cp -r ground-first ~/.claude/skills/

# Method 2: Symlink for updates
ln -s /path/to/ground-first ~/.claude/skills/ground-first
```

Then invoke with `/ground` or `/ground-first` in any Claude Code session.

### OpenAI Codex

```bash
# Copy to your Codex skills directory
cp -r ground-first ~/.codex/skills/
```

Invoke with `$ground` or `$ground-first`.

### Any LLM (ChatGPT, Gemini, etc.)

Use the [quick-start one-liner](#quick-start--no-coding-needed) above as a system prompt or first message. Works anywhere — no install needed.

---

## Usage

```
/ground                    → activate with default mode (full)
/ground lite               → lightweight mode, one-line assumption only
stop grounding             → deactivate
```

### Modes

| Mode | Triggers on | Output | Web Search | Token Overhead |
|------|------------|--------|------------|----------------|
| `lite` | HIGH only | One inline sentence | If needed | ~10–20 tokens |
| `full` *(default)* | MEDIUM+HIGH | Full grounding block | When needed | ~50–150 tokens |

---

## What Triggers Grounding

| Signal Type | Examples |
|-------------|---------|
| Platform-specific trends | "that TikTok sound", "Instagram filter everyone uses" |
| Viral/trending content | "the meme where X", "that video everyone shared" |
| Slang / colloquial | Gen-Z terms, regional language, abbreviations |
| Named cultural phenomena | "Brat summer", "quiet quitting", "brain rot", "demure" |
| Niche communities | Game meta, fandom references, hobby jargon |
| Recent events | Anything that may be after training cutoff |
| "Everyone knows" framing | "you know that thing where..." |
| Implicit pop culture refs | Anything where a plausible-but-wrong interpretation exists |

---

## Repo Contents

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill — works in Claude Code, OpenAI Codex, Gemini CLI |
| `evals/evals.json` | Test cases documenting real failure modes |
| `evals/CONTRIBUTING.md` | How to add a test case (no coding needed) |
| `examples/` | Real eval results comparing with vs. without |

---

## Prior Art & Inspiration

This skill builds on top of existing work — hat tip to:

- **[grill-me](https://github.com/mattpocock/skills)** by Matt Pocock — forces understanding before implementation (planning/design focus)
- **Anthropic's "ground-first prompting"** — official technique for long-context document grounding
- **Web search tool patterns** — search-before-answering for knowledge-cutoff issues

The gap `ground-first` fills: an automatic, portable skill that *detects* culturally-specific/trending references and *triggers web search grounding* before responding. No existing skill does this generically.

---

## Why This Matters for Real-Time Context

LLMs are trained on a snapshot of the world. By the time you're talking to them:

- That viral TikTok trend from last week isn't in their training data
- That slang term your friends use has evolved
- That meme has been remixed 50 times since they last saw it

`ground-first` bridges the gap: **it turns your LLM into a real-time-aware assistant** by triggering targeted searches exactly when the context demands it.

---

## Contributing

PRs welcome. Especially interested in:
- New context-risk signal patterns
- Platform-specific adaptations
- Non-English slang detection improvements
- Eval results from your own tests

---

## License

MIT — use it, remix it, ship it.

---

*Built with the [Claude Code Skills system](https://docs.anthropic.com/en/docs/claude-code). Compatible with any LLM.*
