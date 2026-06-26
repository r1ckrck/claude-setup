# Design system — spec

**Purpose.** Record the decisions and intended behavior of the visual system — typeface choices
and roles, color character and roles, the accent rule, motion behavior, component behavior, and
spatial approach — as reasoning.

**Hard boundary.** This doc says *which* and *why* and *how it behaves*. It never specifies hex
values, px/rem/ms numbers, scale ratios-as-numbers, CSS variable names, or component code — those
are produced in the code phase. A number is a defect here. Every decision must trace to a brand
attribute or a design principle.

**Brief-aware:** motion and color recommendations adapt to the brief's ambition — an expressive
brief points to motion as a lead medium and bolder color; a restrained brief to functional motion
and near-mono. **Concept-gated:** color, light/dark, and layout commonly wait on the site concept —
if it isn't chosen, defer them with `> Deferred — <what's needed>` and trace each to the concept
once it lands.

## Interview

### Typography

#### [CHOICE] Typeface strategy
- One family, weight does the work — **(Recommended — enacts hierarchy by weight and restraint)**
- Two: a display face + a workhorse text face
- Two: a sans for UI + a mono for code/technical signature — **(Recommended for a design engineer — mono quietly signals the engineering half)**

#### [OPEN] Typeface rationale
> "Name the typeface(s) you're drawn to and, one line each, why it fits the brand — what does it
> say before anyone reads a word?"

#### [CHOICE] Type scale approach (intent, not numbers)
- Tight, restrained scale — few sizes, contrast by weight and space — **(Recommended — resists size sprawl)**
- Generous editorial scale — wide range, large display moments

### Color

#### [CHOICE] Palette character
- Near-monochrome + one accent — **(Recommended — lets the accent and the work carry the meaning)**
- Warm neutral foundation + accent (paper/ink)
- Cool/technical neutrals + accent

#### [OPEN] The accent
> "Your one accent, conceptually — and its job. Define what it marks (e.g. 'the single most
> important action,' 'the live thing'), not a decoration. One line on why this color."

#### [CHOICE] Semantic role coverage to define now (by job, not value)
- Minimal — text, surface, accent
- Standard — + states (success/warning/danger/info) — **(Recommended — states are unavoidable; define each by job, e.g. "danger = irreversible action")**
- Full — + borders, muted text, elevated surfaces

#### [CHOICE] Light / dark intent
- Light only
- Dark only
- Both, with stated intent — **(Recommended — note dark is not an inversion; the accent must be re-judged per mode)**

### Motion

#### [CHOICE] Motion philosophy
- Functional only — motion explains state changes
- Functional + sparing expressive moments — **(Recommended — informs and focuses, with one or two signature beats)**
- Expressive throughout

#### [OPEN] Motion behavior
> "One or two lines: how motion should feel and what it's allowed to do, e.g. 'quick, eased,
> always tied to a real state change; never autoplay or loop; respects reduced-motion.'"

### Components

#### [OPEN] Universal behavior bar
> "What must be true of every interactive component, regardless of which one? e.g. 'visible focus
> state; identical behavior everywhere; every async action has loading, empty, and error states.'"

#### [CHOICE] State-coverage commitment
- Core states (default/hover/focus/disabled)
- Core + async (+ loading/empty/error) — **(Recommended — empty and error states are where polish shows)**

### Layout & spacing

#### [CHOICE] Spatial approach (intent)
- Consistent rhythm from one base unit — **(Recommended — calm and consistent without naming numbers)**
- Looser, composition-by-eye

#### [OPEN] Layout character
> "One line: dense or airy, centered editorial column or full-bleed, grid-strict or asymmetric —
> and what carries hierarchy when color is mostly absent?"

## Outline
1. Intent — this records decisions and behavior; values live in the code phase.
2. Typography — typeface(s) + role of each + why; scale as intent.
3. Color — palette character; roles by job; the one-accent rule and the accent's purpose; light/dark intent.
4. Motion — philosophy; behavior; reduced-motion stance.
5. Components — universal behavior bar; committed state coverage.
6. Layout & spacing — spatial rhythm; layout character; what carries hierarchy.

## Acceptance test
- [ ] Zero tokens — no hex, px/rem/ms, ratio numbers, CSS variable names, or component code.
- [ ] Every typeface entry states a role and a rationale.
- [ ] Color defines roles by job; the one-accent rule is explicit with the accent's purpose named.
- [ ] If dark mode is in scope, it's stated as re-judged intent, not inversion.
- [ ] Motion names what it may do and must not, plus reduced-motion.
- [ ] Components name a universal behavior bar and an explicit state-coverage list.
- [ ] Spacing is a single rhythm/intent, not a numeric scale.
- [ ] Every decision traces to a brand attribute or a principle.
- [ ] The code phase could start building without re-deciding anything conceptual.
