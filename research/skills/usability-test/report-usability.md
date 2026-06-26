# Report contributions — usability test

What this cartridge contributes to the combined processed report. The whole-report shape is in `facilitator/report-scaffold.md`; this file defines the test-specific bits.

## Stats this test contributes

```json
{
  "success_counts":  { "success": N, "fail": N, "assisted_success": N },
  "severity_counts": { "0": N, "1": N, "2": N, "3": N, "4": N },
  "assists_per_run": [N, N, N, N, N, N, N, N],
  "avg_turns":       N,
  "run_verdicts":    { "valid": N, "give_up": N, "blocked": N, "invalid": N }
}
```

## Charts this test produces

Rendered by `facilitator/charts.py`:

- `success_rate` — success / assisted-success / fail (horizontal bar)
- `severity_dist` — NN/g severity distribution

## Findings axes (Cross-user findings section)

1. **Task outcomes** — what succeeded, what failed, where assists were needed
2. **Path divergence** — where each persona went off the optimal route
3. **Hesitation patterns** — where users paused, re-read, doubted
4. **What worked** — elements that performed well across personas (not optional)

## Snapshot card fields (per persona)

Free-form paragraph: task outcome (success / assisted / fail) + path taken (compact, show divergence) + failure point if any + assists used and their level + severity + verdict. Standout blockquote with the user's most diagnostic line.

## Craft notes

- **Severity scale (NN/g).**

| Level | Meaning |
|---|---|
| 0 | Not a usability problem |
| 1 | Cosmetic — fix only if time allows |
| 2 | Minor — low priority |
| 3 | Major — high priority to fix |
| 4 | Catastrophe — must fix before release |

: NN/g severity rubric for usability runs.

- **Problem-forward unit.** Issue (what couldn't be done) → Evidence (observation + verbatim quote / turn reference) → Severity → Recommendation (one specific design move).
- **"What worked" is not optional.** Report elements that performed well, not only problems. Stops reports from reading as one-sided.
- **Assists are data.** Log every assist with its level (per facilitator's Graduated assistance ladder); never hide them. An assisted-success is reported separately from an unassisted-success.
- **Recommendations.** Follow `facilitator/SKILL.md → Recommendations discipline`. Design moves, never gating.

Grounded in: NN/g severity ratings; Rubin & Chisnell.
