---
name: atelier
description: Decide the tech stack for a website or web-app build, the opinionated dependency-light way. Triage how much stack a project actually needs, then route to the right framework, libraries, server, and payments — each with a default, alternatives, and combination rules. Use when starting a new site/app, scoping a build, choosing a library for a capability (motion, 3D, charts, forms, auth, payments…), or asking "what stack should I use for X". Copy-and-own over install-and-depend.
---

# atelier

A stack-decision framework. Given a build, decide **how much** stack it warrants and **which** pieces to reach for — filtered through an opinionated doctrine: dependency-light, copy-and-own, one source-of-truth per project, named rules of thumb.

Two principles run through everything:

- **Rule of least power** — the simplest stack that meets the project's real constraints. Don't lay down a framework, a server, or a kit the project hasn't earned.
- **Copy-and-own > install-and-depend** — prefer vendoring source (shadcn-registry, copy-paste) over npm dependencies. Import only irreducible engines (motion, three, gsap, an auth lib). Be wary of kits that drag transitive deps you won't use.

**These are suggestions, not mandates.** Everything below — the tiers, the defaults, the rules of thumb — is an opinionated starting point, not a gate. The project decides; override anything when it calls for something else.

## How to use this skill

1. **Triage** the project into a tier (below). This decides which layers activate.
2. **Apply Base** (always) + the **Scaffold** forks for that tier.
3. **Pull the Capability / Server / Payments** doctrine cards the project needs — read only the relevant files.
4. **Weigh the rules of thumb** on each card (combination, ordering, dependency posture).

Read the deeper files on demand — don't load them all:

| File | Holds |
|---|---|
| `reference/base.md` | The universal spine + locked rules (incl. tokens-everywhere) |
| `reference/scaffold.md` | Once-at-start forks: token pipeline, repo shape, deploy, testing |
| `reference/modules/<name>.md` | One capability doctrine card each |
| `reference/server.md` | Backend, by kind, + stack recipes |
| `reference/payments.md` | Payments, by scenario |

## Layer 0 — Triage

Classify the project before choosing anything. Framing is solo-maker: **lifespan · interactivity · data · surfaces** — not team size.

Ask, in order:
1. **Lifespan / SEO** — does it live more than a few weeks, or need to be found by search?
2. **Interactivity** — beyond links and scroll, does it need client state or forms?
3. **Persistence / auth** — does it store data or have accounts (talks back to a server)?
4. **Commerce** — does it sell something?
5. **Surfaces** — more than one app sharing code?

The first "yes" that escalates sets the tier:

| Tier | Project shape | Stack it warrants | Layers active |
|---|---|---|---|
| **T0 · Throwaway** | one-off slide, mockup, experiment, 404 | Plain HTML/CSS + a `tokens.css`. No framework, no build | Base (minimal) |
| **T1 · Static site** | portfolio, landing, marketing, docs | Next SSG (or Astro if zero-JS is the goal) · Tailwind+tokens · shadcn · light motion | Base · Scaffold · some Capability |
| **T2 · Interactive** | client state, forms, light personalization | Next App Router (hybrid render) · Capability modules · maybe a BaaS read | + more Capability |
| **T3 · App + backend** | accounts, auth, DB, persistence, API | Next full-stack · a Server kind · DB/ORM/auth | + Server |
| **T4 · Platform/product** | multi-surface, monorepo, sells something | Everything, incl. token pipeline + monorepo | + Server + Payments |

A tier activates its row and the rows above it. Don't reach past the tier unless the project needs it — a T1 site usually won't touch `reference/server.md`.

## The unit — a doctrine card

Every capability / server kind / payment option is written as:

```
When      → the trigger that makes you reach for this
Default   → best-in-class pick
Reach for → alternatives + the specific condition that selects each
Rules     → rules of thumb for combining / ordering — suggestions, not gates
Deps      → vendor (copy-and-own) vs import (irreducible engine)
Tier      → minimum tier this belongs to
```

Read the card, take the default unless a "reach for" condition fires, and weigh the rules of thumb. The opinion is the point — not the list.

## Growing the doctrine

Rules are earned, not pre-written. When a real build surfaces a clash or a preference, add it to the relevant card. Defaults shift as the ecosystem moves; treat every card as current-state, revisited when a build proves it wrong.
