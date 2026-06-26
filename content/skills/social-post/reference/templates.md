# Template picker

Map content shape → template. All 10 templates live in `renderer/src/templates/`; visual specs and ASCII sketches in `docs/surfaces/social.md`.

## Composition model

Templates are thin: a `SlideFrame` + a layout shell (`CenterStage` · `VisualOverCaption` · `SequenceStack` · `SplitColumns` · `FreeStage`) filled with atoms. Need a layout the ten presets don't cover? Compose a new one from a shell + atoms rather than forcing a preset — see `renderer/CLAUDE.md`. Every template accepts `index` / `total` (carousel indicators) and `mode` (`"light"` default · `"dark"`).

## Decision table

| Template | Best fit | Bad fit |
|---|---|---|
| **HeroTitle** | Carousel opener · statement post · standalone title slide · series cover | Diagram-heavy content; anything that needs a supporting visual |
| **HeroTitleMinimal** | Pure typographic statement · the "deleted the abstraction" moment | When supporting body copy or a hairline-divided summary line is needed |
| **DiagramAnchored** | Tool explainers · system breakdowns · workflow overviews · anything where a diagram does the work | Pure-text observations; no visual artifact |
| **ProcessFlow** | Step-by-step explainers · numbered workflows · "1.OPEN → 2.FILL → 3.SHIP" pieces | Non-sequential ideas; comparisons; single-stat moments |
| **StackPoster** | Layered architectures · "the stack" posts · L01 → L08 systems read as a tower | Linear processes (use ProcessFlow); two-state comparisons |
| **ClosingSummary** | Carousel closer · "save this if it changed how you think" · takeaway slide with optional CTA-to-consider | Opening slides; mid-carousel slides |
| **QuoteReference** | Curated find pillar · single-thought posts · attributed quote with body context | Build logs; technical breakdowns |
| **StatFocus** | One number IS the message · build-log outcome stats · conversion lift / time saved / error reduction | Multi-number comparisons; qualitative findings |
| **Comparison** | Failure-pivot pillar · "tried X, now Y" · before/after two-column · trade-off naming | Three-or-more way comparisons; non-binary states |
| **CodeFocus** | Build-log fix moments · the snippet IS the centerpiece · "this useId() call killed the bug" | Code as illustration only — embed inline in DiagramAnchored body instead |
| **AnnotatedImage** | Tool reviews · UI breakdowns · screenshot with callout arrows + margin notes pointing at parts | Conceptual diagrams (use DiagramAnchored); raw images without commentary |

## Carousel sequence patterns

A carousel is 3–5 slides per `docs/voice.md`. Common shapes:

| Sequence | Slides | Use |
|---|---|---|
| **Hook → Process → Close** | HeroTitle · ProcessFlow · ClosingSummary | Workflow posts; how-I-did-it pieces |
| **Hook → Stack → Close** | HeroTitle · StackPoster · ClosingSummary | "The stack" posts; system explainers |
| **Hook → Diagram → Body → Close** | HeroTitle · DiagramAnchored · DiagramAnchored · ClosingSummary | Tool deep-dives where two angles of the diagram matter |
| **Stat → Story → Method → Close** | StatFocus · DiagramAnchored · ProcessFlow · ClosingSummary | Build-log with a headline number |
| **Before → After → Lesson** | Comparison · Comparison · ClosingSummary | Failure-pivot pieces |
| **Find → Context → Why** | QuoteReference · DiagramAnchored or AnnotatedImage · ClosingSummary | Curated find pillar |

Default: **Hook → Process → Close (3 slides)**. Expand only when the content warrants — never pad.

## Variant notes

- **HeroTitle vs HeroTitleMinimal** — Minimal is bare display + sign-off; HeroTitle adds a hairline + body line. Pick Minimal when the title is the whole composition.
- **StatFocus vs Comparison** — StatFocus is one number; Comparison is two states. If the answer is "compared to what?", it's Comparison.
- **DiagramAnchored vs AnnotatedImage** — DiagramAnchored draws a structural diagram (boxes, arrows, stack). AnnotatedImage points at a real screenshot or image.
- **ProcessFlow vs StackPoster** — Process is sequential (1 → 2 → 3). Stack is layered (L01 below L02 below L03). Process flows horizontally; Stack reads vertically.
- **CodeFocus vs code in DiagramAnchored** — CodeFocus when the snippet is the story. Inline code blocks for code as supporting detail only.

## Anti-patterns

- Don't mix template grammars in one carousel without a reason — three different sequence shapes back-to-back reads as random.
- Don't use HeroTitle for slides 2+ — the hero is the opener; repeating display-scale text dilutes it.
- Don't pick a template because it looks cool — pick because the content shape demands it.
