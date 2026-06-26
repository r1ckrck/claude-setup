# Report contributions — concept test

What this cartridge contributes to the combined processed report. The whole-report shape is in `facilitator/report-scaffold.md`; this file defines the test-specific bits.

## Stats this test contributes

```json
{
  "verdict_counts":      { "validate": N, "iterate": N, "kill": N },
  "comprehension_counts":{ "correct": N, "partial": N, "missed": N },
  "would_use_counts":    { "yes": N, "maybe": N, "no": N },
  "binding_constraints": [
    {"persona": "Name", "category": "...", "detail": "..."},
    ...
  ],
  "run_verdicts":        { "valid": N, "give_up": N, "blocked": N, "invalid": N }
}
```

`would_use_counts` is captured but not charted (folded into snapshot cards). Invalid / give-up / blocked excluded from pies; surfaced in the run-verdicts table.

## Charts this test produces

Rendered by `facilitator/charts.py`:

- `verdict_pie` — validate / iterate / kill distribution
- `comprehension_dist` — correct / partial / missed (horizontal bar)
- `binding_constraints_bar` — aggregated by constraint category

## Findings axes (Cross-user findings section)

Use these as `####` subsections in §5:

1. **Comprehension** — how each persona described it back; surface-correct vs deep-correct
2. **Relevance** — use cases (rescue / routine / none); honest no vs polite no
3. **Desirability** — anchored affect words, where the politeness trap fired
4. **Objections** — binding constraints per user (reference back to §2 table)

## Snapshot card fields (per persona)

Free-form paragraph carrying: comprehension level + would-use call + key affect word + binding constraint + verdict. Closes with a standout user-voice blockquote.

## Craft notes

- **Politeness trap.** Personas, like people, praise to be polite. Do not record *"looks nice"* / *"clean"* / *"modern"* as desirability — these are politeness filler. Report only reactions backed by a reason or a concrete use. Treat hedging (*"maybe"*, *"I guess"*, *"if it actually worked"*) as soft-negative. Flag in-line.
- **Verdict scale (per persona).** validate (would adopt as-is) / iterate (would adopt if specific objections addressed) / kill (won't adopt for this use case). The persona-level verdict stays honest signal. The rolled-up *report-level recommendations* must still follow facilitator's *Recommendations discipline*.
- **Insight unit.** Each finding = Insight (one-line claim) → Evidence (verbatim quote / observation) → So-what (implication for the concept).
- **Recommendations.** Follow `facilitator/SKILL.md → Recommendations discipline`. Design moves, never gating.

Grounded in: NN/g concept testing; Microsoft Desirability Toolkit (Benedek & Miner); Fitzpatrick (politeness trap).
