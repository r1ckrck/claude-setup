# Server-state / data fetching

**When** → the UI reads/writes remote data and needs caching, revalidation, or optimistic updates.

**Default** → **TanStack Query** — caching, background refetch, mutations, the standard for client server-state.

**Reach for**
- **SWR** — lighter needs; simple read-and-revalidate.
- **Server Actions** (Next) — mutations and form submits first-party, no client data lib needed.

**Rules**
- Don't reach for a data lib if **Server Components + Server Actions** already cover the read/write — least power.
- Keep server-state (TanStack Query) separate from client UI state (see `state.md`); don't put fetched data in Zustand.

**Deps** → **import** (small).

**Tier** → T2+ (client data), T3+ when it's backed by a real server.
