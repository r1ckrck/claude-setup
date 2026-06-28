# Scaffold — the once-at-start forks

Decided once, at `git init`. These are structural; changing them later is expensive, so choose deliberately per tier.

## Token pipeline

The mechanism for the locked tokens-everywhere rule (see `base.md`). Stay dependency-light; escalate only when design-sync demands it.

| Mechanism | Source of truth | Figma sync | Fits |
|---|---|---|---|
| **Tailwind v4 `@theme` + CSS vars** *(default)* | `globals.css` / `tokens.css` | manual export | T1–T3 — zero extra deps; shadcn themes ride these vars |
| Plain CSS custom properties | `tokens.css` | none | T0 |
| **Tokens Studio + Git** | JSON in repo | bi-directional | T3–T4 when a designer syncs tokens from Figma |
| **Style Dictionary** | JSON + transforms | via plugin | T4 multi-platform / design-system pipeline |

Default reasoning: Tailwind v4's `@theme` keeps tokens as CSS variables in one file with no build step and no dependency, and shadcn's theming already consumes CSS vars — so the spine and the tokens align for free. Reach for Tokens Studio only when tokens must round-trip with Figma, and Style Dictionary only when one token set feeds multiple platforms (web + mobile + docs).

## Repo shape

| Shape | When |
|---|---|
| **Single repo** *(default)* | one app; nothing shared |
| **Turborepo + pnpm workspaces** | 2+ apps share code/types, or a design-system package feeds multiple surfaces (T4) |
| Nx | only at large scale with enforced architecture / codegen needs |

Signal you do **not** need a monorepo: no shared code, or it lives in one npm package; no coordinated cross-app changes.

## Deploy

| Target | When |
|---|---|
| **Self-hosted — Ubuntu · Forgejo (CI/CD) · Caddy** | own-the-box default; full control |
| Vercel | when Next-native edge/preview flows or zero-ops deploy matter more than ownership |

## Testing

**Playwright** — end-to-end and visual. Added once the project has behavior worth protecting (T2+).
