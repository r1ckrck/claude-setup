# Motion

**When** → elements need to move: component transitions, shared-element morphs, scroll choreography, page transitions.

**Default** → **Motion** (`motion`, by Framer) — declarative, React-native, covers ~90% of UI animation (gestures, layout, `AnimatePresence` exit).

**Reach for**
- **GSAP** — timeline/scroll sequencing, complex story-driven choreography, fine imperative control.
- **View Transitions API** — page/route transitions and shared-element morphs (a card *becomes* its page). Native, no library.
- **Lenis** — smooth-scroll on inner/long pages.
- **AutoAnimate** — trivial list/layout shifts where a full engine is overkill.

**Rules**
- Prefer **CSS / View Transitions first** — reach for an engine when CSS can't express it.
- Lean to **one motion engine per page** — mixing Motion and GSAP tends to jank (competing rAF loops).
- Honor **reduced-motion**.
- Favor motion that carries meaning over decoration.

**Deps** → **import** (Motion / GSAP / Lenis are irreducible engines). View Transitions is native (no dep).

**Tier** → T1+ (light), heavier choreography typically T2+.
