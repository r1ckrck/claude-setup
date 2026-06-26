# Report scaffold — processed report (markdown)

The markdown half of the two-artifact output. Plain GFM. No build pipeline, no front-matter — this file is a read deliverable in its own right, alongside the PDF rendered from `report-scaffold.html`. Each cartridge contributes the test-specific bits (stats schema slice + chart inventory + findings axes + snapshot fields + craft notes) via its own `report-<test>.md`.

The section order mirrors `report-scaffold.html` one-to-one — same content shape, different syntax.

## Authoring rules

- **No YAML front-matter, no LaTeX-aware blocks, no markset-specific syntax.** The PDF comes from HTML, not this file.
- **No hedges.** Strip "notably / importantly / the data shows / it's worth noting / crucially". Write as a research lead briefing colleagues.
- **Locked persona order** throughout: Arsheen → Danish → Mohammed → Seema → Akeela → Himanshu → Salman → Sonal.
- **Recommendations discipline** (see `facilitator/SKILL.md`) — design moves, never gating decisions.
- **Inference is required.** Output of inference must be design opportunities.

## Section template

```markdown
# <Display title — e.g. "Ask AI pill">

**<Test-type> · <Date>**

| Field | Value |
|---|---|
| Test | <Test type — e.g. "Concept test — Ask AI pill"> |
| Stimulus | <Short phrase — screen / URL / topic> |
| Date | <e.g. "1 June 2026"> |
| Protocol | <e.g. "Parallel + lockstep · 1 adaptive round + debrief"> |
| Run verdict | <e.g. "8 of 8 valid"> |

**Users (locked order, India-1 / India-2 / India-3 segments):**

| User | Segment | City |
|---|---|---|
| Arsheen | India-1 | Pune |
| Danish | India-2 | Delhi |
| Mohammed | India-2 | Hyderabad |
| Seema | India-2 | Mumbai |
| Akeela | India-3 | Lucknow |
| Himanshu | India-3 | Indore |
| Salman | India-3 | Kanpur |
| Sonal | India-3 | Noida |

---

## <N> things stakeholders should know

3–5 numbered findings — each = a load-bearing observation, not a recommendation.

### 1. <One-line headline>
One supporting sentence, max two.

### 2. <Next headline>
…

> **Run-level verdict:** **VALIDATE / ITERATE / KILL.** One sentence stating why.

### Binding constraint per user

The single objection that would have to be removed for adoption.

| User | Binding constraint | Category |
|---|---|---|
| Arsheen | <constraint> | <category> |
| … | | |

---

## Method

1. **<Step name>** — one sentence.
2. **<Step name>** — one sentence.
3. **<Step name>** — one sentence.
4. **<Step name>** — one sentence.

---

## The numbers

One block per chart in the cartridge's inventory. PNG embed + 1-line headline + 1-sentence supporting context.

![Verdict distribution](artifacts/charts/verdict_pie.png)

**<Headline number / observation.>** One supporting sentence.

![Comprehension on first encounter](artifacts/charts/comprehension_dist.png)

**<Headline.>** One sentence.

![Binding constraints by category](artifacts/charts/binding_constraints_bar.png)

**<Headline.>** One sentence.

---

## What surfaced across users

Organized by the cartridge's findings axes. Concept: comprehension / relevance / desirability / objections. Each axis = one `###` with a one-line punch + 2–4 specific observations.

### <Axis name>

<One-line punch.>

- <Specific observation>
- <Specific observation>
- <Specific observation>

### <Next axis>

…

---

## What each user said

One block per persona, in locked order. Each: ~30–40-word read + a standout verbatim quote. End the read with the load-bearing observation, not the play-by-play.

### Arsheen — India-1, 30, Pune · **Kill**

<Two sentences. Synthesis, not play-by-play.>

> *"<One verbatim line that captures the snapshot.>"*

### Danish — India-2, 37, Delhi · **Iterate**

…

(continue through Sonal)

---

## What to build

Numbered design moves the team can ship. **Follow Recommendations discipline** — never gating decisions; expand options, don't constrain them. Persona-tag each with `(driven by X, Y)`.

### 1. <Imperative headline of the design move>

Two sentences — what to build, who it unblocks, why it expands options.
*(driven by Persona, Persona)*

### 2. <Next>

…

### N. <Adjacent finding — re-frame X>

Adjacent-finding recommendations (from observations outside the focal stimulus) get a final position and an explicit *Adjacent —* prefix.
*(driven by all 8 / specific list)*

---

## Verdict by user

| User | Run | <Test-specific verdict — e.g. "Concept" / "Severity"> | Why |
|---|---|---|---|
| Arsheen | valid | Kill | One-line reason. |
| Danish | valid | Iterate | One-line reason. |
| Mohammed | valid | Iterate | … |
| Seema | valid | Iterate | … |
| Akeela | valid | Kill | … |
| Himanshu | valid | Iterate | … |
| Salman | valid | Iterate | … |
| Sonal | valid | Kill | … |

---

Verbatim conversations and debriefs — `<stem>_transcripts.md`.
```

## Section count reference (matches HTML scaffold)

| # | Section | HTML class |
|---|---|---|
| 1 | Cover (title + subtitle) | `.cover` |
| 2 | Header card (metadata + stimulus) | `.header-grid` |
| 3 | Personas | `.personas` |
| 4 | Executive summary (N findings + verdict callout) | `.findings` + `.verdict-callout` |
| 5 | Binding constraint per user | `.constraints-table` |
| 6 | Method | `.method-strip` |
| 7 | The numbers | `.stat-card` |
| 8 | What surfaced across users | `.findings-axes` / `.axis` |
| 9 | What each user said | `.snapshots` / `.snapshot` |
| 10 | What to build | `.recs` / `.rec` |
| 11 | Verdict by user | `.verdicts-table` |
| 12 | Footer / transcripts pointer | `footer` |

For interview runs, omit the stimulus image (header card has metadata only); the rest of the structure holds.
