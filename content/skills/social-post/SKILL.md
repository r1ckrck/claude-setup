---
name: social-post
description: Turn a brief into a rendered social post — carousel (Instagram primary) + standalone post.md (LinkedIn + X + Instagram caption) + optional video. Use when the user says "draft a post about X", "make a social post", "carousel about Y", "post on LinkedIn about Z", "make a reel of X", or invokes anything that produces output under social/.
allowed-tools: Read, Edit, Write, Bash
---

# Social post

Orchestrator. Reads the brief, applies voice + design rules, picks template(s), drives the renderer, writes the post copy. Output is a self-contained folder under `social/<YYMMDD-slug>/` that ships to Instagram, LinkedIn, and X from one invocation.

## Skills this depends on

- **`remotion`** — invoke before any work inside `renderer/`. Composition authoring, registration in `renderer/src/Root.tsx`, render commands. This skill orchestrates; `remotion` knows the renderer.

## Read first (in order)

1. `docs/voice.md` — load-bearing. Pillars, hook definition, anti-bait checks, per-platform length budgets. Never skip.
2. `docs/design.md` — visual system. Color, type, motifs, accent rule.
3. `docs/surfaces/social.md` — canvas sizes, type scale, the 10 layout templates with ASCII sketches.
4. `renderer/CLAUDE.md` — renderer day-to-day workflow.
5. `reference/templates.md` — only when picking a layout.
6. `reference/render.md` — only when rendering.
7. `reference/post-writing.md` — only when drafting `post.md`.

## Inputs

The skill accepts two shapes:

| Input | What happens |
|---|---|
| **Brief** — topic + angle + key points | Draft the copy from scratch using `docs/voice.md`; user reviews before render. |
| **User-supplied draft** — full or partial copy | Skip drafting. Voice pass + carousel split + render. |

Default: assume brief unless the user pastes copy.

## Output shape

```
social/<YYMMDD-slug>/
├── source/
│   └── <Composition>.tsx          # the React composition (Remotion)
├── carousel/
│   ├── 01.png · 02.png · ...      # IG-primary carousel slides
├── video.mp4                      # only when the brief calls for motion
└── post.md                        # standalone post — see reference/post-writing.md
                                   # three sections: Instagram · LinkedIn · X
                                   # conveys the same story; works without the carousel
```

Naming: `YYMMDD-kebab-slug`. Slug from the post's headline, not the topic. The slug also renders onto each carousel slide bottom-left per `docs/design.md` bottom-margin convention.

## Flow

1. **Read** `docs/voice.md`, `docs/design.md`, `docs/surfaces/social.md`, `renderer/CLAUDE.md`.
2. **Confirm brief** — restate the topic / angle / pillar fit (`build log` / `process note` / `tool stack` / `failure-pivot` / `curated find`) and the design lens. If the user supplied a draft, skip drafting.
3. **Draft copy** — write the post text first (it's the load-bearing artifact). Pointer: `reference/post-writing.md`. Get user sign-off on copy before building visuals.
4. **Pick template(s)** — choose carousel sequence (typically 3–5 slides). Pointer: `reference/templates.md`.
5. **Author composition** — invoke the **`remotion`** skill. Write `<Composition>.tsx` under `social/<slug>/source/`, register in `renderer/src/Root.tsx`.
6. **Preview in Studio** — `cd renderer && npm run dev` → `localhost:4242`. User reviews the carousel before render.
7. **Render stills** — pointer: `reference/render.md`. Output to `social/<slug>/carousel/01.png`, `02.png`, …
8. **Render video** (when applicable) — pointer: `reference/render.md`. Output to `social/<slug>/video.mp4`.
9. **Write `post.md`** — pointer: `reference/post-writing.md`. Three sections (Instagram · LinkedIn · X) sized to each platform's length budget from `docs/voice.md`.
10. **Show outputs** — list rendered files. User iterates by going back to step 3, 4, or 5 as needed.

## Hard rules

- **Design lens, every time.** Every post answers "why is a designer the right person for this?" If it can't, it doesn't go up. (`docs/voice.md`)
- **Never improvise voice.** If `docs/voice.md` is silent on a question, ask the user — don't guess.
- **No engagement bait.** Hooks ≠ bait. `docs/voice.md` carries the difference.
- **One accent moment per piece.** `docs/design.md` accent rule applies to every carousel slide.
- **Sign-off + slug on every visual.** Bottom-margin convention from `docs/design.md`.

## Out of scope

- Slides — use `slide-deck`.
- Long-form blog / docs — different surface, different voice.
- Auto-publishing — files are written; manual posting from each platform.
- Per-platform A/B copy variants — V1 ships one post.md with three platform sections.
- Image generation for embedded assets — use `fal-image` separately if a unique image is needed inside the carousel.
