# Tech stack — spec

**Purpose.** Fix the base technical foundation the portfolio is built on — rendering model,
framework, language, content source, backend, hosting, and (after tokens exist) styling,
components, and motion. Decisions and rationale only — no code, no token files.

**Sequencing.** Decide-early layers gate the rest: rendering, framework, language, content source,
backend, hosting. Decide-after-tokens layers wait until the design-system decisions exist:
styling, components, motion. The reason: design tokens are the source of truth and the styling tool
consumes them — never pick the styling tool before tokens exist.

Ask the constraints prompt first; it can override any default below.

**Brief-aware:** read the brief's ambition. An awards-level / expressive brief points to a richer
interactive stack (a React meta-framework, real motion tooling); a lean, content-first brief
points to a static-first stack. Recommend accordingly rather than defaulting to one.

### [OPEN] Constraints (ask first)
> "Any existing preferences or hard constraints — languages/frameworks you know or must use,
> hosting you're tied to, a need for live/interactive demos, deadlines?"

## Decide early

### [CHOICE] Rendering model
- Static site generation (SSG) — **(Recommended — fast, cheap, secure; portfolios are mostly static content. Deviate if you need per-request server logic)**
- Server-side rendering (SSR)
- Single-page app (SPA)
- Hybrid

### [CHOICE] Framework
- Astro — **(Recommended — islands + zero-JS by default suit content-heavy portfolios that still want interactive demos. Trade-off: smaller ecosystem than Next)**
- Next.js (React) — deviate here if you want one React app with heavy interactivity
- SvelteKit
- Vite + React (no meta-framework)

### [CHOICE] Language
- TypeScript — **(Recommended — type safety pays off even solo; the ecosystem default. Trade-off: minor setup overhead)**
- JavaScript

### [CHOICE] Content source (for case studies)
- Markdown/MDX in-repo — **(Recommended — versioned with the code, no external service; MDX allows interactive embeds. Trade-off: edits need a commit)**
- A CMS
- Hardcoded in components

### [CHOICE] Backend / server side
- None — static + a form service for contact — **(Recommended — a contact form doesn't justify a server. Trade-off: dynamic features need a service later)**
- A lightweight backend (forms, auth, dynamic data)

### [CHOICE] Hosting / deploy
- A static host (Cloudflare Pages / Netlify / Vercel) — **(Recommended — Cloudflare Pages for unmetered bandwidth on static; Vercel if you chose Next.js)**
- Self-hosted
- Plus a custom domain

## Decide after tokens

### [CHOICE] Styling
- Tailwind (v4, CSS-variable-native, maps cleanly onto tokens) — **(Recommended for speed + token alignment. Trade-off: utility classes in markup)**
- CSS Modules
- vanilla-extract
- Plain CSS

### [CHOICE] UI / component approach
- Headless/unstyled primitives (Radix, Base UI) — **(Recommended for a designer who wants full visual control with accessibility handled)**
- Hand-built components
- A styled kit (shadcn/ui) as a scaffold to restyle, not a default look

### [CHOICE] Animation / motion
- CSS-only transitions/animations — **(Recommended — matches restrained motion; no JS weight. Trade-off: complex sequences are harder)**
- A JS library (Motion / Framer Motion) for orchestrated sequences
- GSAP for heavy timeline work

## Outline
1. Constraints.
2. Decide-early decisions (rendering, framework, language, content, backend, hosting), each with rationale + trade-off.
3. Decide-after-tokens decisions (styling, components, motion), each with rationale + trade-off.
4. A short trade-offs note for anything deferred or uncertain.

## Acceptance test
- [ ] Every layer is decided, each with a rationale and a named trade-off.
- [ ] Each decision is marked decide-early or decide-after-tokens.
- [ ] Dependency direction is correct (styling/components/motion come after tokens).
- [ ] Anything deferred says so honestly.
- [ ] A developer could scaffold the project from this doc alone.
- [ ] No code, no token values.
