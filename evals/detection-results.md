# Detection Accuracy — Results

> **Superseded by the v2 cross-vendor run.** This file held the v1 pilot table
> (single model, one machine, "21/21, 6/6, 100%"). v2 re-ran detection across **6
> vendors × 36 cases × 3 runs = 648 calls** through one identical harness, and the
> numbers came down — see [`../BENCHMARK.md`](../BENCHMARK.md) for the honest headline
> and [`metrics.json`](metrics.json) for every computed figure.

The raw per-call data is in [`detection_results.json`](detection_results.json); regenerate
all metrics with:

```bash
python analyze.py detection_results.json metrics.json
```

## v2 headline (pooled across all 6 vendors)

| | sensitivity | specificity | balanced acc |
|---|---|---|---|
| all categories (held-out test) | 0.50 | 1.00 | **0.75** |
| scoped to targeted categories (test) | 0.75 | 1.00 | **0.875** |

Specificity is **0.94–1.00 across every vendor** (the "stays out of the way" claim,
proven cross-vendor). Sensitivity splits hard by category: trend/slang/recency score
high; ambiguous-intent / stack-context / regional barely fire across *all six* vendors —
either a roadmap gap or a sign those cases need a clarifying question, not a web search.
[`../BENCHMARK.md`](../BENCHMARK.md) argues both readings.
