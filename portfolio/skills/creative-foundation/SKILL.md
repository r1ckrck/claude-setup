---
name: creative-foundation
description: >
  Define the foundation of a portfolio or creative project before any build — through a guided
  interview where you draft and the user decides. Use this whenever the user says "set up my
  portfolio foundation", "define my portfolio", "start my portfolio", "creative foundation",
  "what should my portfolio be", "help me figure out my positioning / narrative / brand", "create
  design principles", "define my design system", "pick a tech stack for my site", or wants to
  decide the concept, story, look, feel, and base build of a portfolio — even if they don't say
  "skill". Interview the user with multiple-choice questions that each carry a recommended option,
  plus open prompts for their full vision; draft each document; let the user confirm before moving
  on; then wire CLAUDE.md to link the set. Source-agnostic — never assumes any specific input
  files exist. Concept and decisions only — no tokens, CSS, or component code (that is the build).
allowed-tools: Read, Write, Edit, AskUserQuestion, Bash(python3 .claude/skills/creative-foundation/scripts/wire.py:*)
user-invocable: true
---

# creative-foundation

Define a portfolio's foundation — what it is, who it's for, how it looks, feels, reads, and is
built — as a set of documents in a `foundation/` folder, authored before any code. The split
mirrors the other skills: this skill is the *how* (the interview, the specs, the rules); the
`foundation/` folder is the *what* (the decided documents).

The skill **interviews → drafts → confirms → wires**. For each document it asks the user a short
set of questions, drafts the document from the answers, lets the user review and edit, then moves
on. When the documents exist, it updates `CLAUDE.md` so the router points at them.

Source-agnostic: nothing here assumes a specific person, account, or input file. Draw material
from whatever the user provides or from the conversation. Decisions and reasoning only — tokens,
CSS, and components belong to the build phase, not here.

## Pre-flight

1. **Gather context (optional).** Invite the user to share any existing material — a resume, past
   work, notes, an old site. It is input to draw on, never assumed; the skill stays source-agnostic
   and works fine with nothing.
2. **Resolve the output folder.** Documents go in `foundation/` (override with `--foundation` or
   `$CREATIVE_FOUNDATION`). Run `wire.py scaffold` to create the folder and heading-only skeletons;
   it never overwrites a file that already has content.
3. **Confirm the run shape.** The default is all nine documents in order. The user may do a
   subset or revisit one later — each document stands on its own.

## The interview model

Every document is produced through a short interview, never a blank page. Two question types,
mixed per document:

- **Choice questions** — 2–4 concrete options, one marked **Recommended** with a one-line why,
  plus an always-present "something else." Use `AskUserQuestion`. These let the user move fast on
  decisions with established good answers.
- **Open prompts** — free text, for vision, voice, story, and taste, where the user's own words
  are the point. Ask conversationally; let them write as much as they want.

Always offer both: a choice question's "something else" opens a free field; an open prompt can
offer starter options to react to. Never trap the user in the options.

Per-document loop: **interview → draft the document → user reviews and edits → confirm → next.**
Earlier documents stay revisable; when one changes, flag the documents downstream that inherit
from it.

More that makes the interview work:

- **Rounds.** Ask choice questions in rounds of **≤4** (AskUserQuestion's cap); ask open prompts
  conversationally.
- **Calibration over pick-one.** Answers are often blends — capture the nuance ("this spine, that
  flavor") rather than forcing a single option.
- **Signature sentences.** For the lines that carry the whole foundation (the proposition, hook,
  throughline, stakes), offer several worded options and iterate until each is locked.
- **Deferral.** Any decision can be parked: write `> Deferred — <what it's blocked on>` in the
  document and record candidate directions as seeds. `wire.py` surfaces these as Open threads.
  Never block the rest of the foundation on one decision.

## Carry the brief forward

Before each later stage, re-read the brief and bias the recommended option to its **ambition**
(restrained ↔ awards-level) and **intent** (job search / showcase / clients). Recommendations
adapt to the brief — they are not fixed defaults. A recommendation that ignores the brief is a
defect.

## Workflow

Six stages. Each loads its spec from `references/` and produces its document. Load a spec only
when you reach its stage.

| Stage | Loads | Produces |
|---|---|---|
| A · Intent | `references/brief.md` | `foundation/00-brief.md` |
| B · Position & story | `references/positioning.md`, `references/narrative.md` | `01-positioning.md`, `02-narrative.md` |
| C · Content | `references/content-plan.md` | `03-content-plan.md` |
| D · Design | `references/brand.md` → `concept.md` → `design-principles.md` → `design-system.md` | `04-brand.md`, `05-concept.md`, `06-design-principles.md`, `07-design-system.md` |
| E · Tech | `references/tech-stack.md` | `08-tech-stack.md` |
| F · Wire | — | updated `CLAUDE.md` |

Stage D is ordered: brand sets the personality, the **concept** is the keystone idea that expresses
it, principles set the decision filter, the design system embodies them. Each design document cites
the one before it. The concept **gates** color, light/dark, and layout (design system) and the IA
(content plan); it is often the biggest creative task and may be deferred — defer it and the
dependent sections with the marker rather than stalling the run.

`references/craft.md` holds the shared quality bar (the reversibility test, "even over",
"from → to", the token boundary, the read-aloud voice test, and the cross-doc coherence check).
Apply it throughout, and run the coherence check after all documents exist.

## The documents

| Document | What it fixes |
|---|---|
| `00-brief.md` | Audience, intent, goals, success criteria, scope |
| `01-positioning.md` | The claim you win on, with proof |
| `02-narrative.md` | The story arc that carries the positioning |
| `03-content-plan.md` | Information architecture, voice, project-display rules |
| `04-brand.md` | Attributes, personality, art direction |
| `05-concept.md` | The novel organizing idea — the keystone (gates color, layout, IA) |
| `06-design-principles.md` | The decision filter (4–7 principles) |
| `07-design-system.md` | Typography, color, motion, components — conceptual |
| `08-tech-stack.md` | The base build: rendering, framework, language, hosting |

## Authoring rules

- **Source-agnostic.** Never assume a specific input file exists; ask or draw from the conversation.
- **Current state only.** No meta-comments — no "previously," "v2 of," "changed from," "TBD."
- **Small counts, rationale per item.** Principles 4–7, brand attributes 3–5; every item carries
  a one-line "because." There is no separate decisions log.
- **Token boundary.** The design-system document records decisions and behavior, never values
  (no hex, px, ms, CSS variables, or component code).
- **One home per concern.** Voice lives in the content-plan; the brand holds personality and art
  direction; the narrative holds the story.
- **Router discipline.** `CLAUDE.md` stays a thin router — links by path, no eager imports, no
  duplicated facts.

## Wiring CLAUDE.md

Once documents exist, run:

`python3 .claude/skills/creative-foundation/scripts/wire.py wire`

It regenerates one delimited block (`<!-- creative-foundation:start -->` … `:end -->`) listing
every foundation document with its title and one-line description. Content outside the markers is
untouched; if `CLAUDE.md` is absent it creates a minimal router. Re-run it whenever documents are
added or their descriptions change. Any `> Deferred — …` markers in the documents are collected
into an **Open threads** list in the same block, so parked decisions stay visible.

## Out of scope

No working-style document. No work selection or project cataloguing (that is the `project-vault`
skill). No case-study templates beyond the content-plan's display rules. No decisions log. No
design tokens, CSS, or component code — those are the build.
