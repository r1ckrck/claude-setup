# Writing `post.md`

`post.md` is the text artifact. It works *with* the carousel and *without* it. On X and LinkedIn it carries the whole message. On Instagram it sits below the carousel as caption. Same idea, three platform-sized shapes.

## Voice is non-negotiable

Pointer to `docs/voice.md`. Re-read every time. The rules below are field application — they don't replace the source.

## File shape

```markdown
# <Headline used as slug>

## Instagram

<IG caption — short; the carousel does the visual work>

<hashtags: 3–5 tight tags>

## LinkedIn

<LinkedIn post — 100–250 words>

## X

<X post — 100–200 words, let it breathe>
```

Three sections. Same core idea, scaled to each platform's length budget (from `voice.md` per-platform shape table).

## Per-platform length budgets

From `docs/voice.md`:

| Platform | Length | Hook | Hashtags | CTA |
|---|---|---|---|---|
| **Instagram** | Caption short; carousel carries the message | First slide (visual) is the hook | 3–5 tight tags | None |
| **LinkedIn** | 100–250 words | Strong first line | 0 | None |
| **X** | 100–200 words — let it breathe | First post stands alone | 0 | None |

## Hook (the first line)

Definition + hook-vs-bait examples live in `voice.md` → "Hook — definition". Always read that before drafting.

Quick test: read your first line alone. Would a stranger want the second line? If no, rewrite.

## Anti-AI checks (must pass all)

These are the most common ways AI-drafted copy reads as AI. Each check is binary — pass or fail.

| # | Check | How to test |
|---|---|---|
| 1 | **No three-part rhetorical structures** | Search for "not X, not Y, but Z" rhythms — recognizable AI cadence. Cut to one clause. |
| 2 | **No corporate adjectives** | grep for: `powerful`, `seamless`, `leverage`, `unlock`, `transform`, `robust`, `cutting-edge`, `next-level`, `game-changer`, `revolutionary`. Zero hits. |
| 3 | **No throat-clearing openers** | First sentence isn't "Today I want to talk about…", "Let me tell you about…", "Here's something I learned…". Cut to the hook. |
| 4 | **No rhetorical-question endings** | Last sentence isn't a question to the reader. The post ends with a statement that lands. |
| 5 | **Specific over abstract** | At least one of: file name, number, command, named tool, named choice. If none, the post is too vague. |
| 6 | **Reads aloud naturally** | Read it out loud. If you wouldn't say it to a friend over coffee, rewrite it. |
| 7 | **No engagement bait** | No "drop a 🔥", "thoughts?", "agree?", "you won't believe", "this one trick". |
| 8 | **No listicles** | No "5 things I learned", "10 tips for…". Voice rules forbid the form. |
| 9 | **No emoji** | Zero. `voice.md` is absolute on this. |
| 10 | **Trusts the reader** | Doesn't over-explain. Doesn't summarize what was just said. Doesn't repeat the carousel back to the reader. |

If any check fails, rewrite — don't ship.

## Carousel-and-post relationship

| Rule | Why |
|---|---|
| Post conveys the same story as the carousel, not a description of it | Carousel might never load (X, LI). Post must stand alone. |
| Never write "swipe to see more" or "as shown in the carousel" | Engagement bait + couples the post to the visual. |
| If the carousel has a single key number / phrase, the post can echo it | Reinforcement is fine; restating slide-by-slide is not. |
| Post passes the dinner-table test independently | If you told this to someone over dinner without showing them anything, does it land? |

## Hashtag rule

Only Instagram. 3–5 tight tags. Pull from the pillar and the topic — not generic (`#design`, `#ai` too broad). Examples that fit voice: `#designengineer`, `#claudecode`, `#remotion`. Avoid: trend tags, joke tags, tags-for-reach.

## Pillar fit — declare it in your head

Every post fits one (or two overlapping) pillars from `voice.md`:

- **Build log** — what I made this week, messy parts included
- **Process notes** — how I think when design + code meet
- **Tool stack** — what I use / switched / avoid
- **Failure / pivot** — what didn't work, what I changed
- **Curated find** — one thing worth your time

If you can't name the pillar, the post isn't ready.

## Design lens (the gate)

The hard gate. Definition lives in `voice.md` → "The design lens — non-negotiable". If a post can't answer "why is a designer the right person for this?" — it doesn't ship.

## Final checklist

- [ ] Pillar named
- [ ] Design lens visible
- [ ] Hook works as standalone first line
- [ ] All 10 anti-AI checks pass
- [ ] Three sections written (X · Instagram · LinkedIn)
- [ ] Each section within length budget
- [ ] IG hashtags present (3–5 tight tags)
- [ ] Reads aloud naturally
- [ ] Post works without the carousel
