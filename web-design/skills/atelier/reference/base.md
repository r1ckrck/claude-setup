# Base — the universal spine

Applied on every build at or above its tier. The pieces here are the usual starting point — the defaults reached for on most builds, not a fixed mandate.

## The spine

| Layer | Choice | Notes |
|---|---|---|
| Framework | **Next.js (React)** | the single spine across tiers; Astro only when zero-JS static is the explicit goal (T1) |
| Language | **TypeScript** | always |
| Styling | **Tailwind v4** | CSS-variable-native; carries the tokens |
| Primitives | **shadcn (copy-and-own) + Radix** | own the component source; accessibility handled |
| Class utils | **cva · clsx · tailwind-merge** | the `cn` pattern shadcn expects |
| Icons | **one set — Lucide or Phosphor** | pick one per project, don't mix |
| Rendering | **static-first, hybrid** | pages prebuild; a route server-renders only when it needs to |

T0 drops the framework and ships hand-written HTML/CSS — but still leans on the tokens default below.

## Standing default — tokens everywhere

Reach for **one source-of-truth token file** on every project, T0 included. This is the strong default — a deliberate deviation is fine; drifting into hardcoded values by accident is what it guards against.

- **No hardcoded CSS values.** Color, space, radius, type, shadow, motion timing — all read from tokens.
- **Change once → changes everywhere.** Editing the token file restyles the whole project.
- **Scoped per project.** Each project owns its tokens; nothing is shared across projects.

The *mechanism* (how the token file is authored and consumed) is a Scaffold choice — see `scaffold.md`. The *default* is set here.

## Dependency posture

The default is **copy-and-own**:

- **Vendor** (copy the source, own it): component kits, shadcn primitives, copy-paste snippets, any small/stable thing you'll modify.
- **Import** (npm dependency): only irreducible engines — the animation/3D/auth/data libraries you'd never reimplement.
- **Avoid**: kits that pull transitive dependencies you won't use. The win is killing bloat, not eliminating npm.

When vendoring vs importing is a genuine call: vendor when the code is small, stable, and you'll modify it; import when it's a large, actively-maintained engine — vendoring that means owning its maintenance, which is worse than the dependency.
