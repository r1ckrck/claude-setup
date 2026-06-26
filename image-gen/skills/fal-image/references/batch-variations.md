# Batch variations — fal-image

How to produce multiple variations of a concept by rotating one component of the 5-component formula while holding the others constant. Routes here when the user asks for "N variations", "options", "variants", or "alternatives."

---

## When to use

- User asks for multiple versions of the same concept: "give me 4 variations", "show me 3 options", "make me a few different takes"
- User wants to A/B between style choices: "show me a moody version and a bright version"
- User is iterating on a hero image and wants to see different lighting / mood / composition options

---

## The rotation principle

A batch is **N generations where one formula slot rotates and the others stay locked**. This isolates a single variable so the user can compare like-for-like.

| Slot rotated | What stays constant | Use case |
|---|---|---|
| **Style + Lighting** (default) | Subject, Action, Location, Composition | "Show me different moods of the same scene" |
| **Composition** | Subject, Action, Location, Style | "Show me different framings of this product" |
| **Action** | Subject, Location, Composition, Style | "Show me different poses of the same character" |
| **Location/Context** | Subject, Action, Composition, Style | "Show me the same product in different settings" |
| **Subject** | rarely useful as a rotation — defeats the purpose of "variations of X" | — |

**Default rotation: Style + Lighting.** Most batch requests want mood/aesthetic exploration.

---

## Picking the rotation slot

If the user specifies what should vary, use that:
- "different moods" → Style+Lighting
- "different angles" → Composition
- "different settings" → Location
- "different poses" → Action

If they don't specify, ask one MCQ:

```
What should vary across the variations?
   a) Mood / lighting / overall style (recommended)
   b) Camera angle / framing / composition
   c) Setting / location / background
   d) Pose / action of the subject
```

This counts toward the 3-MCQ cap.

---

## Constructing N variations

The orchestrator passes the same locked context to brief-constructor N times, each with a different value for the rotation slot. brief-constructor returns N distinct prompts.

### Example — Style+Lighting rotation, N=3

User: *"3 variations of a coffee shop hero image"*

Locked context:
- Subject: "weathered ceramic espresso mug, single-origin shot, marbled crema"
- Action: "resting on worn oak counter, single wisp of steam"
- Location: "small-batch roastery, mid-morning"
- Composition: "45° hero, 80mm Hasselblad at f/2.8, shallow depth of field"

Rotated Style+Lighting values:

| Variation | Style + Lighting |
|---|---|
| **v01** | "warm directional natural light from camera-right with white-card fill, true-to-life color, Kinfolk magazine editorial register" |
| **v02** | "moody single-source key from above with deep shadows falling away, late-evening warm tungsten quality, low-key cinematic register" |
| **v03** | "bright high-key soft daylight from a large window, clean shadowless fill, contemporary advertising register, Wallpaper* design feature" |

brief-constructor builds 3 separate prompts, the orchestrator calls fal 3 times, saves 3 outputs.

---

## Naming convention

Batch outputs share the slug and increment versions as usual:

```
generated/images/2026-04-25/
├── coffee-shop-hero-v01.png   ← variation 1 (warm Kinfolk)
├── coffee-shop-hero-v01.json
├── coffee-shop-hero-v02.png   ← variation 2 (moody cinematic)
├── coffee-shop-hero-v02.json
├── coffee-shop-hero-v03.png   ← variation 3 (bright Wallpaper*)
└── coffee-shop-hero-v03.json
```

Each sidecar's `params.batch_index: <n>` and `params.batch_total: <N>` and `params.batch_rotation: "style+lighting"` records that this was part of a batch.

---

## Cost reporting

Total cost = N × per-image cost. Report it explicitly after the batch completes:

> "Batch of 3 variations done. Cost: 3 × $0.05 = **$0.15**. Outputs at `generated/images/2026-04-25/coffee-shop-hero-v01.png` through `v03.png`."

If any single variation fails (fal error), the orchestrator reports partial success: "2 of 3 succeeded. v02 failed with [error]. Cost: $0.10 for the 2 successful." No retries on failed variations unless user asks.

---

## Limits

- **N capped at 6 by default.** More than 6 starts costing real money fast and rarely helps decision-making. If user explicitly asks for >6, confirm cost first.
- **Same model across all variations** — don't mix models within a batch. Apples-to-apples comparison requires identical model.
- **Same seed is NOT used** — each variation uses a fresh seed so they're genuinely different. (If user wants seed-locked variations, that's a different request: "regenerate with seed X but vary Y.")
