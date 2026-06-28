# Global / client state

**When** → UI state that several components share and props/context can't cleanly carry (lens/intent, panel open-close, active selection).

**Default** → **Zustand** — tiny, unopinionated store.

**Reach for**
- **Jotai** — atomic state, fine-grained derivations.
- **nanostores** — cross-framework / island architectures.

**Rules**
- Try **React state + context** first; reach for a store only when prop-drilling or context churn actually hurts.
- **Don't** store server data here — that's TanStack Query's job (see `data.md`).
- Keep stores small and scoped; one global mega-store is a smell.

**Deps** → **import** (all tiny).

**Tier** → T2+.
