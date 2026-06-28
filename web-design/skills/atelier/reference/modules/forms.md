# Forms & validation

**When** → any input the user submits: contact, auth, settings, multi-step flows.

**Default** → **react-hook-form + Zod** — smallest feature-complete form lib, best TS inference, and what shadcn's form components use out of the box. Zod is the schema/validation default.

**Reach for**
- **Valibot** — when bundle size matters; tree-shakable, Zod-like API (≈30-min switch).
- **TanStack Form** — deeply nested dynamic forms / complex multi-step wizards where strict compile-time field-name safety pays off.

**Rules**
- One schema drives both runtime validation and the TypeScript type — don't hand-maintain a parallel type.
- Validate on the server too (server action / API) — client validation is UX, not security.
- Reach for TanStack Form only when RHF's ergonomics actually break down; it's a heavier, evolving API.

**Deps** → **import** (small, irreducible). The form markup (shadcn fields) is vendored.

**Tier** → T2+.
