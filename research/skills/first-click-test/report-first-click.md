# Report contributions — first-click test

What this cartridge contributes to the combined processed report. The whole-report shape is in `facilitator/report-scaffold.md`; this file defines the test-specific bits.

## Stats this test contributes

```json
{
  "destination_counts":  { "<element_name>": N, ... },
  "optimal_path_counts": { "correct": N, "correct_indirect": N, "incorrect": N },
  "severity_counts":     { "0": N, "1": N, "2": N, "3": N, "4": N },
  "turns_to_click":      [N, N, N, N, N, N, N, N],
  "run_verdicts":        { "valid": N, "give_up": N, "blocked": N, "invalid": N }
}
```

## Charts this test produces

Rendered by `facilitator/charts.py`:

- `first_click_destination_pie` — where each persona tapped first
- `severity_dist` — NN/g severity distribution (horizontal bar)

## Findings axes (Cross-user findings section)

1. **Where eyes went first** — competing elements, banner-pulls, label-clarity wins
2. **Why there** — verbatim reasoning per persona
3. **Goal-shape mismatches** — when the right tile lost to a louder competing element

## Snapshot card fields (per persona)

Free-form paragraph: first element tapped + 1-line *"why there"* + optimal-path call (correct / correct-indirect / incorrect) + severity 0–4 + verdict. Standout blockquote with the user's *"why there"* line.

## Craft notes

- **Severity (NN/g, applied inversely).** A wrong first click on a primary task is high-severity.

| Level | First-click outcome |
|---|---|
| 4 | Wrong click on the only path to a critical task |
| 3 | Wrong but recoverable |
| 1–2 | Correct click but slow or uncertain |
| 0 | Correct and confident |

: Severity rubric for first-click runs.

- **Problem-forward unit.** Goal given → First click → Optimal path → Time-to-first-click → Why there (verbatim) → Downstream implication → Severity.
- **Competing elements.** Name what pulled attention from the optimal target (banner, brighter CTA, identity-fit imagery). This is often the load-bearing insight.
- **Recommendations.** Follow `facilitator/SKILL.md → Recommendations discipline`. Design moves, never gating.

Grounded in: MeasuringU / Optimal Workshop (first-click metrics); NN/g severity.
