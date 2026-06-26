# Render commands

## Use the `remotion` skill

**Before any work inside `renderer/` — invoke the `remotion` skill.** It carries Remotion best practices: composition shape, fps/frames, render flags, gotchas. This file covers only the assistant-specific wiring on top.

## Author the composition

Composition source lives **with the post**, not inside `renderer/src/`:

```
social/<YYMMDD-slug>/
└── source/
    └── <CompositionName>.tsx
```

Use PascalCase for component / composition names. A composition is built one of two ways:

- **From a template preset** — import one of the ten layouts from `renderer/src/templates/` and pass props. Covers most slides.
- **From a shell + atoms** — when no preset fits, compose a `SlideFrame` from `renderer/src/shells/` filled with atoms from `renderer/src/components/`. The shell owns layout; atoms own content. See `renderer/CLAUDE.md` for the shell + atom catalog.

Relative path from the post's `source/`: `../../../renderer/src/templates/HeroTitle` (templates three levels up; `shells/` and `components/` sit alongside `templates/`).

## Per-slide props

Both templates and `SlideFrame` accept:

| Prop | Effect |
|---|---|
| `index` + `total` | Carousel position. Both set (with `total > 1`) renders the whisper-weight progress bar + swipe chevron; the chevron drops on the last slide (`index === total - 1`). Omit for a standalone slide. |
| `mode` | `"light"` (default) or `"dark"`. Sets the palette for the whole slide. One mode per piece — not per-slide alternation. |
| `slug` | The bottom-left reference mark. Matches the post folder name. |

```tsx
<ProcessFlow {...props} slug="<slug>" index={1} total={5} mode="light" />
```

## Register in `renderer/src/Root.tsx`

Add one import + one `<Composition>` per slide that needs to render. The renderer uses one composition per rendered output (so a 3-slide carousel = 3 compositions, one per slide).

```tsx
import { HeroSlide } from "../../social/<slug>/source/HeroSlide";

const COMMON = { durationInFrames: 30, fps: 30, width: 1080, height: 1350 } as const;

<Composition id="<slug>-01" component={HeroSlide} {...COMMON} />
```

Studio hot-reloads. The composition appears in the left sidebar.

## Preview in Studio

```bash
cd renderer
npm run dev
# → http://localhost:4242
```

Click the composition in the sidebar. User reviews before render.

## Render a still

From the assistant root:

```bash
cd renderer
npx remotion still <CompositionId> ../social/<slug>/carousel/NN.png
```

`NN` is the zero-padded slide number (`01`, `02`, ...). Output path is relative to `renderer/`.

For a multi-slide carousel, render each composition in sequence — same command, one per slide.

## Render a video

```bash
cd renderer
npx remotion render <VideoCompositionId> ../social/<slug>/video.mp4
```

Video compositions need `durationInFrames` calibrated for the desired length at the chosen fps. Defer to the `remotion` skill for fps / duration / encoding decisions.

## Output canvas sizes

Per `docs/surfaces/social.md`:

| Surface | Canvas | Composition `width × height` |
|---|---|---|
| Instagram carousel (default) | 4:5 portrait | 1080 × 1350 |
| Instagram square | 1:1 | 1080 × 1080 |
| LinkedIn single image | 1.91:1 | 1200 × 627 |
| X | 16:9 | 1600 × 900 |

Default is 1080 × 1350. Other sizes only when the brief explicitly calls for them.

## TypeScript check

After authoring or modifying compositions:

```bash
cd renderer
npx tsc --noEmit
```

Must exit 0 before rendering. Type errors in Root.tsx break Studio entirely.

## Common pitfalls

- **Forgot to register in Root.tsx** — composition won't appear in Studio, render command fails with "composition not found".
- **Wrong relative path from `social/<slug>/source/`** — `renderer/src/templates/` is three levels up: `../../../renderer/src/templates/`.
- **Hand-edited the rendered PNG path** — always write to `social/<slug>/carousel/NN.png`, not anywhere else. The slug on the visual must match the folder name.
- **Skipped Studio preview** — silent layout regressions are common. Always preview before rendering all slides.
