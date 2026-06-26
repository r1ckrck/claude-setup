---
name: distill
description: Turn the current planning conversation into one structured markdown — Goal, Decisions locked, and explicitly-flagged Open questions — saved as a markdown file in the project's docs/ folder as a source-of-truth doc you can grow into a PRD. Use whenever the user says "distill this", "write this up", "capture our decisions", "turn this into a doc", "make a brief", or has had a long back-and-forth worth saving — even without the word "distill". Works for any project type: design, 3D, code, writing. Synthesizes what's already been said; never re-interviews, and flags anything undecided rather than guessing at it.
---

# distill

Turns a sprawling planning conversation into one clean source-of-truth document — every real decision captured, every hole made loud. The point is not a tidy summary; it's a doc that never looks more settled than it is, so you can see exactly what's still yours to decide before it becomes work.

Synthesize what's already in the conversation. Don't re-interview the user, and don't invent decisions that weren't made — if something is unresolved, it's a gap, not a guess.

## How it works

1. **Read the conversation back** — the whole thread, plus any files or links it referenced. Understand what was actually being decided.
2. **Separate decided from open** — sort every point into one bucket or the other. A leaning that was never confirmed is *open*, not decided.
3. **Fit it to the document shape** below — one point per line, plain language.
4. **Flag the gaps** — collect the open points into the **Open** section and mark any inline reference to an unresolved choice with `▸ needs decision`.
5. **Save** to `docs/<slug>.md` (see Saving).
6. **Report back in two lines** — the path it wrote, and the top open questions it still needs from the user.

## The document

Use this exact shape. Drop any section that has no content — **except Open, which always appears**, even if only to say "nothing open."

```
# <goal title>

## Goal
What we're trying to achieve — 1–2 lines.

## Context
Why this, for whom, and the constraints that bound it.

## Decisions locked
What's been settled. One decision per line.

## Open — needs your call
What is NOT decided yet. The load-bearing section — never omit it.

## Approach
How we'll do it, if that was discussed.

## Out of scope
What we're deliberately not doing.

## Next step
The single immediate next action.
```

## Flagging gaps

- **Open is always present** — a doc with an empty Open section is suspicious; if nothing is open, say so explicitly.
- **Inline marker `▸ needs decision`** — drop it wherever the text leans on a choice that hasn't been made, so the gap is visible in context, not just listed at the bottom.
- **Never write "TBD"** — name the actual missing decision instead. Vague placeholders hide the hole.
- **Unsure → gap** — if you can't tell whether something was decided, it goes in Open. Don't resolve ambiguity by guessing.

## Saving

- Write to **`docs/<slug>.md`**, relative to the current project — it lands in whatever repo the skill runs in. Create `docs/` if it doesn't exist.
- **Slug** is kebab-case from the goal (e.g. "auth flow decisions" → `docs/auth-flow.md`).
- **If the file already exists, update it in place** — merge new decisions, refresh the Open section, keep prior locked decisions — never silently overwrite. The doc is meant to grow across a project.

## Principles

- **Agnostic** — assume nothing about code. The same shape serves a design system, a 3D print, or an essay.
- **Only real decisions** — capture what was actually concluded, nothing aspirational.
- **Gaps louder than decisions** — seeing what's missing is the whole value; surface it, don't bury it.
- **Scannable** — short lines, plain words; the user reads this to act, not to admire.
- **Not `capture-smart`** — that routes inbox notes into brain files; `distill` synthesizes one live conversation into one planning doc. Different jobs.
