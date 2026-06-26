---
name: slide-deck
description: Orient to the slides/ project — static HTML decks with shared tokens, fonts, icons, and primitives. Use when the user says "work on the slides", "add a slide", "create a new deck", "scaffold a deck", "edit the <deck> deck", "QA the deck", or invokes anything that touches assistant/slides/.
allowed-tools: Read, Edit, Write, Bash
---

# Slide deck authoring

A briefing skill. Points Claude at the slides project so it can work inside `slides/` following established conventions. Does not draft content, does not apply social voice rules, does not publish.

## Read first

Before touching anything: read `slides/CLAUDE.md`. That file is the source of truth for the DOM contract, style contract, asset references, and editing rules. This skill is a pointer to it, not a replacement.

## Where things live

| Path | What |
|---|---|
| `slides/CLAUDE.md` | Operational rules — DOM contract, style contract, editing rules |
| `slides/shared/tokens.css` | Design tokens (symlink → `docs/tokens.css`) — single source of truth |
| `slides/shared/design-system.css` | Slide chrome, cards, flowchart primitives (`.fc-*`, `.card`, `.flow-step`, …) |
| `slides/shared/core.js` | Viewport scaler, keyboard / click / hash nav, fullscreen |
| `slides/shared/fonts/` | Symlink → `assets/fonts/` |
| `slides/shared/icons/` | Symlink → `assets/icons/` |
| `slides/shared/monogram/` | Symlink → `assets/monogram/` |
| `slides/shared/textures/` | Symlink → `assets/textures/` |
| `slides/<deck>/index.html` | Deck entry — links shared CSS + deck CSS + core.js |
| `slides/<deck>/slides.css` | Deck-specific layouts only |
| `slides/<deck>/CLAUDE.md` | Deck-specific content rules (optional) |
| `slides/qa/qa.js` | Playwright screenshot + nav harness |

## Two modes

### New deck

User wants a fresh deck. Read `reference/scaffold.md` for the step-by-step playbook and copy-paste-ready templates.

### Existing deck

User wants to edit, extend, or add a slide. Read in this order:

1. `slides/CLAUDE.md` — global contracts
2. `slides/<deck>/CLAUDE.md` (if present) — deck content rules
3. `slides/<deck>/slides.css` — existing layout conventions
4. `slides/<deck>/index.html` — existing slide patterns

Match the existing patterns. Reach for shared primitives (`.fc-*`, `.card`, `.flow-step`, …) before writing bespoke CSS. Promote a class from `slides.css` to `shared/design-system.css` only when ≥2 decks use it.

## Run / preview

```bash
cd assistant/slides
python3 -m http.server 8765
# → http://localhost:8765/<deck>/
```

Keyboard nav: arrows / space / `f` for fullscreen. Hash routing supports `/#5` to land on slide 5.

## QA

```bash
node qa/qa.js <deck>            # screenshots @ 1920×1080 / 1440×900 / 1280×720 + nav battery
node qa/qa-debug.js <deck> [n]  # dump deck transform / rect for slide n (default 5)
rm -rf qa/shots                 # cleanup after reviewing
```

QA fails on any console error, pageerror, or HTTP ≥400. A clean summary is necessary but not sufficient — visually review the PNGs in `qa/shots/<deck>/`. Layout regressions are silent.

## Inline-SVG flowcharts

Use `.fc-*` shared classes (`.fc-term`, `.fc-proc`, `.fc-dec`, `.fc-arrow`, `.fc-arrow-bold`, `.fc-arrow-dashed`, `.fc-hero`, plus `.fc-*-text` / `.fc-phase-*` for SVG text). **Each `<marker id="arr-…">` must be unique per SVG** (e.g. `arr-light`, `arr-light-2`, …) — Chromium has a cross-SVG marker bug.

## Editing rules

- Decide first: design-system change (affects every deck) or deck-only? Edit the right file.
- Don't move a class from `slides.css` to `design-system.css` unless ≥2 decks use it.
- Don't add tokens for one-off values; if it's truly one-off, inline it.
- Tokens come from `docs/tokens.css` — change them there, not in `slides/shared/tokens.css`.
- Never reach for raw hex / px. Use `var(--bg-*)`, `var(--text-*)`, `var(--s-*)`, `var(--fs-*)`.

## Out of scope

- Drafting slide content from a brief (the user authors content; the skill scaffolds and wires)
- Voice / tone rules — those are for social posts, not slides
- Publishing, exporting, or deploying decks
- Image generation — use `fal-image` separately
- Visual restyle of existing decks — handled case by case, not as a skill action
