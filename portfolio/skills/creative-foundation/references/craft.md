# Craft — the shared quality bar

The forcing-functions every document spec leans on. They exist to turn nice-sounding words into
real, defendable decisions. When a doc spec says "apply the reversibility test" or "use from→to,"
this is what it means.

## Forcing-functions

**Reversibility test.** A real principle or brand attribute has an opposite a reasonable person
could choose. "Hierarchy by weight, not decoration" is reversible — someone could prefer
expressive maximalism. "Be beautiful" is not — nobody wants ugly. If the opposite is absurd, the
statement is a platitude: sharpen it or cut it. Use on every principle and every brand attribute.

**Even over.** State a principle as "X, even over Y," where both X and Y are genuinely valuable.
This forces a real trade-off instead of a wish. "Depth on a few projects, even over breadth across
many." If Y isn't something anyone would want, the principle has no teeth.

**From → to.** Sharpen a brand attribute by naming the version you mean and the version you reject:
"Not just minimal — minimal as in severe and confident, not minimal as in empty and safe." A bare
adjective is not an attribute until it has a from→to.

**The token boundary (one-directional).** Concepts and the *why* are decided now; concrete values
come later in code. The design-system doc records *which* typeface and its role, *which* colors
play *which* roles, *how* motion should behave — never hex, px, ms, ratios-as-numbers, CSS variable
names, or component code. A number appearing in the design-system doc is a defect.

**Read-aloud test (voice).** Read a sentence out loud. If it doesn't sound like something a human
would actually say, the voice is wrong. The single best check for the voice section.

**Small counts + rationale per item.** Keep sets memorable: 4–7 principles, 3–5 brand attributes,
2–3 motion behaviors. Every item carries a one-line "because" — rationale lives inline, since
there is no separate decisions log.

**Signature sentences.** A few lines carry the whole foundation — the single-minded proposition,
the hook, the throughline, the stakes. Don't draft these once: offer several worded options and
iterate with the user until one is locked. They are worth the rounds.

**Deferral & open threads.** Any decision can be parked. Write `> Deferred — <what it's blocked
on>` in the document where the decision belongs, and record candidate directions as seeds so
nothing is lost. `wire.py` collects every marker into an Open threads list in `CLAUDE.md`. Never
block the rest of the foundation on one unresolved decision.

**Brief-aware recommendations.** Recommendations are not fixed. Before each later stage, re-read
the brief and bias the recommended option to its ambition (restrained ↔ awards-level) and intent
(job search / showcase / clients). A recommendation that ignores the brief is a defect.

**Calibration over pick-one.** Choice answers are often blends, not a single option. Offer the
options, but capture the nuance the user adds — "this spine, that flavor" — rather than forcing one.

## Cross-doc coherence

Run after the docs exist. The foundation is one position told at different scales; the docs must
agree:

- The **brief's** single-minded proposition, the **narrative's** throughline, and the
  **positioning's** claim are the same idea in three voices. If they diverge, one is wrong.
- The same **audience** appears as the brief's target, the positioning's best-fit, and the
  narrative's hero/guide target.
- Every **design-system** decision traces to a **brand** attribute or a **design principle** —
  nothing arbitrary.
- The **voice** (content-plan) matches the **brand** personality — confident brand, confident copy.
- Review the **open threads** — every deferred decision is recorded with what unblocks it.
- The **concept** is what color, light/dark, and layout trace to; until it's chosen, those stay deferred.

The universal smell test: **if a document could belong to someone else's portfolio unchanged, it
is too generic — send it back.**
