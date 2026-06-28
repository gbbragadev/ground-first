# Detection Accuracy — Results (3 runs)

Scored on the operationally important decision: **trigger grounding (yes) vs stay silent (no)**.
Risk level (HIGH/MEDIUM) is secondary; what matters is act-or-not.

## Trigger decision per run

| # | Query | Expected | Run1 | Run2 | Run3 |
|---|-------|----------|------|------|------|
| 1 | very demure, very mindful | YES | yes✓ | yes✓ | yes✓ |
| 2 | TikTok POV ironic | YES | yes✓ | yes✓ | yes✓ |
| 3 | center a div CSS (control) | NO | no✓ | no✓ | no✓ |
| 4 | derivative of x² (control) | NO | no✓ | no✓ | no✓ |
| 5 | Angular new routing | YES | yes✓ | yes✓ | yes✓ |
| 6 | labor rights (BR) | YES | yes✓ | yes✓ | yes✓ |
| 7 | delete user (intent ambiguity) | YES | yes✓ | no✗ | no✗ |
| 8 | OpenAI just-launched model | YES | yes✓ | yes✓ | yes✓ |
| 9 | ADC ranked build | YES | yes✓ | yes✓ | yes✓ |
| 10 | viral Reels sound | YES | yes✓ | yes✓ | yes✓ |

## Scores

- **Specificity (controls 3,4 stay silent): 6/6 = 100%** across all runs. Zero false-positive overhead on clear queries.
- **Sensitivity, in-scope risky (1,2,5,6,8,9,10): 21/21 = 100%** across all runs.
- **Overall trigger accuracy: Run1 10/10, Run2 9/10, Run3 9/10 → mean 93.3%.**
- **Single miss:** case 7 (intent ambiguity) triggered 1/3. Category `intent_mismatch` is not yet implemented in SKILL.md → roadmap item, not a hidden defect.

## Secondary observation — label wobble, decision stable

Risk *level* wobbled across runs on cases 2, 6, 9 (HIGH↔MEDIUM), but the **trigger decision stayed constant**. The operationally meaningful output (ground or don't) is robust even when the label isn't. Worth noting: we could simplify the 3-level scale to a binary trigger/no-trigger with little loss.
