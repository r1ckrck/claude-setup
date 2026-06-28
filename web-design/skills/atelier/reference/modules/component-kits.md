# Component & section kits

**When** → you want pre-built blocks (hero, pricing, bento, marquee, feature sections) instead of hand-building every section.

**Default** → **shadcn/ui** — the base. Owned source, Radix under the hood, themed by your tokens.

**Reach for** (all distribute as copy-in source — install via `npx shadcn add` or paste)
- **Aceternity** — motion-rich, designed-by-an-in-house-team blocks (hero, bento, parallax, glow).
- **Magic UI** — polished micro-interactions and marketing animations (beams, retro grids).
- **Cult** — animated components + AI-product patterns.
- **Origin UI** — large set of advanced primitives.
- Personal shelf: **Skiper**, **React Bits** (animated bits, copy-paste), **Vengeance** (interaction blocks).

**Rules**
- **Suggested priority for marketing heroes: Cult > Skiper > React Bits** — least de-theming first.
- Usually **strip the kit's default theme** before wiring your tokens — no kit ships with your design.
- Prefer copying the one component over pulling a whole kit.
- Prefer blocks that share your motion engine; avoid dropping a GSAP block into a Motion page (see `motion.md`).

**Deps** → **vendor** (registry/copy-paste source you own). The block's animation engine may itself be an import.

**Tier** → T1+.
