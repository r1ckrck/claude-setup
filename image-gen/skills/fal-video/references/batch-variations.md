# Batch Variations — fal-video

How to produce multiple variations of a video concept by rotating one component of the 6-component formula while holding the others constant. Routes here when the user asks for "N variations", "options", "variants", or "alternatives."

---

## When to use

- User asks for multiple versions of the same concept: "give me 3 variations", "show me a couple of options", "make me a few different takes"
- User wants to A/B between camera moves: "show me a slow push-in version and a locked-off version"
- User is iterating on a hero clip and wants to see different motion / mood / composition options

---

## The rotation principle

A batch is **N generations where one formula slot rotates and the others stay locked**. This isolates a single variable so the user can compare like-for-like.

| Slot rotated | What stays constant | Use case |
|---|---|---|
| **Motion** *(default for video)* | Subject, Action, Location, Composition, Style | "Show me different camera moves of the same scene" — push-in vs orbit vs locked-off |
| **Style + Lighting** | Subject, Action, Location, Composition, Motion | "Show me different moods of the same scene" |
| **Composition** | Subject, Action, Location, Motion, Style | "Show me different framings of this product" |
| **Action** | Subject, Location, Composition, Motion, Style | "Show me different gestures of the same character" |
| **Location/Context** | Subject, Action, Composition, Motion, Style | "Show me the same product in different settings" |
| **Subject** | rarely useful — defeats the purpose of "variations of X" | — |

**Default rotation for video: Motion.** Most batch requests for video want to explore the camera-move axis (the most distinctive lever after Style). Mood is a strong secondary default.

---

## Picking the rotation slot

If the user specifies what should vary, use that:
- "different camera moves" / "different motion" → Motion
- "different moods" → Style+Lighting
- "different angles" → Composition
- "different settings" → Location
- "different poses" → Action

If they don't specify, ask one MCQ:

```
What should vary across the variations?
   a) Camera motion / pacing — push-in vs orbit vs locked-off (recommended)
   b) Mood / lighting / overall style
   c) Camera angle / framing / composition
   d) Setting / location / background
```

This counts toward the 3-MCQ cap.

---

## Constructing N variations

The orchestrator passes the same locked context to brief-constructor N times, each with a different value for the rotation slot. brief-constructor returns N distinct prompts.

### Example — Motion rotation, N=3

User: *"3 variations of a coffee shop hero video"*

Locked context:
- Subject: "weathered ceramic espresso mug, single-origin shot, marbled crema"
- Action: "resting on worn oak counter, single wisp of steam"
- Location: "small-batch roastery, mid-morning"
- Composition: "45° hero, 85mm Sony Venice 2 at T2.8, shallow depth of field"
- Style+Lighting: "warm directional natural light from camera-right, true-to-life, Wallpaper* design feature register"

Rotated Motion values:

| Variation | Motion |
|---|---|
| **v01** | "Locked-off frame with slow rack focus over four seconds, gentle drift pacing, subject still — only the steam wisp drifts upward" |
| **v02** | "Slow arc orbit over six seconds, steady drift pacing, subject still — camera circles the mug revealing 270° of the rim" |
| **v03** | "Slow push-in over five seconds, breath-held pacing, subject still — camera drifts from medium close-up to extreme close-up of the marbled crema" |

brief-constructor builds 3 separate prompts, the orchestrator calls fal 3 times, saves 3 outputs.

---

## Naming convention

Batch outputs share the slug and increment versions as usual:

```
generated/videos/2026-04-26/
├── coffee-shop-hero-v01.mp4   ← variation 1 (locked-off + rack focus)
├── coffee-shop-hero-v01.json
├── coffee-shop-hero-v02.mp4   ← variation 2 (slow arc orbit)
├── coffee-shop-hero-v02.json
├── coffee-shop-hero-v03.mp4   ← variation 3 (slow push-in)
└── coffee-shop-hero-v03.json
```

Each sidecar's `params.batch_index: <n>`, `params.batch_total: <N>`, and `params.batch_rotation: "motion"` records that this was part of a batch.

---

## Cost reporting

Total cost = N × per-clip cost. Report it explicitly after the batch completes:

> "Batch of 3 variations done. Cost: 3 × $0.02 = **$0.06**. Outputs at `generated/videos/2026-04-26/coffee-shop-hero-v01.mp4` through `v03.mp4`."

If any single variation fails (fal error), the orchestrator reports partial success: "2 of 3 succeeded. v02 failed with [error]. Cost: $0.04 for the 2 successful." No retries on failed variations unless the user asks.

---

## Limits

- **N capped at 4 by default.** Video runs more expensive than image generation; more than 4 starts costing real money fast on premium models. If user explicitly asks for >4, **confirm cost first** — show "N × per-clip = total" before proceeding.
- **Same model across all variations** — don't mix models within a batch. Apples-to-apples comparison requires identical model.
- **Same seed is NOT used** — each variation uses a fresh seed so they're genuinely different. (If user wants seed-locked variations, that's a different request: "regenerate with seed X but vary Motion.")
- **Same duration / fps / audio** across all variations — only the rotation slot changes. Anything else held constant.
