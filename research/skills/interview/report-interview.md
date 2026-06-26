# Report contributions — interview

What this cartridge contributes to the combined processed report. The whole-report shape is in `facilitator/report-scaffold.md`; this file defines the test-specific bits. No stimulus image; the value is themes and quotes.

## Stats this test contributes

```json
{
  "theme_counts":           { "<theme>": N, ... },
  "quote_counts_per_theme": { "<theme>": N, ... },
  "run_verdicts":           { "valid": N, "give_up": N, "blocked": N, "invalid": N }
}
```

## Charts this test produces

Rendered by `facilitator/charts.py`:

- `theme_frequency_bar` — themes ordered by how many personas surfaced them

## Findings axes (Cross-user findings section)

1. **Themes** — patterns across personas, grouped (not transcript replay); lead with the strongest
2. **Motivations** — what drives behaviour in this area, laddered from what each persona said
3. **Pain points** — concrete frustrations, each with the quote that surfaced it
4. **Topic coverage** — which parts of the topic guide got covered; flag thin spots

## Snapshot card fields (per persona)

Free-form paragraph: dominant theme this persona contributed + their motivation in this domain + any pain point unique to them. Standout blockquote with the persona's most evocative line.

## Craft notes

- **Insight unit.** Theme (pattern, grouped) → Evidence (1–3 verbatim quotes with turn refs) → So-what (implication for design / strategy).
- **Observation vs interpretation discipline.** Always separate. *"Persona said X"* (observation) vs *"[this suggests Y]"* (interpretation). Quotes are exact words.
- **Past behaviour > stated preference.** Chase remembered actions, not opinions. A recalled story outweighs a hypothetical *"would you use this?"*.
- **No stimulus.** Header section in the report omits the right-column image; the `split-65-35` collapses to a single column for interview runs.
- **Recommendations.** Follow `facilitator/SKILL.md → Recommendations discipline`. Design moves, never gating.

Grounded in: Portigal (Interviewing Users); Erika Hall (Just Enough Research); affinity / thematic synthesis.
