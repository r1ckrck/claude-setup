# atelier

A Claude Code skill that decides the tech stack for a website build — *how much* stack a project needs, and *which* pieces to reach for — the opinionated, dependency-light way.

Most stack decisions get re-litigated every project: which framework, which library for motion or charts or auth, how much is too much, what to actually depend on. atelier fixes those decisions in one place an agent (or you) consults at the start of every build.

## How it works

It triages the project first, then routes through layers — loading only what the project earns.

1. **Triage** → classify by lifespan · interactivity · data · surfaces into a tier:

   | Tier | Project | Stack |
   |---|---|---|
   | T0 | one-off / slide | HTML/CSS + tokens |
   | T1 | static site, portfolio | Next SSG · Tailwind · shadcn |
   | T2 | interactive, forms | + capability modules |
   | T3 | app with a backend | + server, DB, auth |
   | T4 | platform, sells something | + payments, monorepo |

2. **Route** → each capability, server kind, and payment option is a **doctrine card**:

   ```
   When · Default · Reach for · Rules · Deps · Tier
   ```

   Take the default unless a "reach for" condition fires; weigh the rules of thumb. Everything is a suggested default — override any card when the project calls for it.

## Two principles

- **Rule of least power** — the simplest stack that meets the real constraints. Nothing the project hasn't earned.
- **Copy-and-own over install-and-depend** — vendor source by default; import only irreducible engines (motion, three, an auth lib). Be wary of kits that drag dependencies you won't use.

## Use it

Clone, then symlink into your skills directory so Claude Code can load it:

```sh
git clone <repo-url> atelier
ln -s "$(pwd)/atelier" ~/.claude/skills/atelier
```

Global (`~/.claude/skills/`) makes it available in every project; a project's `.claude/skills/` scopes it to one. It triggers when you start a build, scope a project, or ask "what stack should I use for X."

## Structure

```
SKILL.md      the skill — triage + routing
reference/    the doctrine cards, read on demand
docs/         design rationale + the research behind the defaults
```

## Make it yours

The defaults encode one maker's taste and stack — React / Next · TypeScript · Tailwind · shadcn. The structure is the reusable part: fork it, swap the defaults on each card, and it becomes *your* decision framework. The opinion layer is the point.
