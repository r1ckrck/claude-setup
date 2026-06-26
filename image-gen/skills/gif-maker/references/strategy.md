# Strategy — gif-maker

When gif-maker is the right skill, how to classify a request into one of 5 intents, and how each intent shapes the downstream parameters (color budget, dither, fal-video domain pick, loop emphasis).

---

## When gif-maker is the right skill

gif-maker generates animated GIFs **from scratch** by orchestrating a fal-video source clip + ffmpeg palette/dither conversion.

Use gif-maker when:
- The user wants a GIF **and has no source video file**
- Trigger phrases: "make a gif of X", "create an animated gif of X", "generate a gif of X", "I need a loading gif", "give me a hero gif"

Do NOT use gif-maker when:
- The user has an existing video file and wants to convert it → **route to `media-processing`**
- The user wants animated WebP / APNG / animated PNG → **route to `media-processing`** (modern-formats reference)
- The user wants a still image → **route to `fal-image`**
- The user wants a video clip (not a GIF) → **route to `fal-video`**

### Disambiguation rule

> *Existing source file → `media-processing`. Needs generation first → `gif-maker`.*

If gif-maker detects that the user references an existing local video file, it should suggest the route:

> "It looks like you have a source video already. `media-processing` can convert it to a GIF directly without paying for a fal generation. Would you like to route there instead?"

---

## Intent classification

5 buckets. Each request maps to exactly one. Detection cues drive the pick; the intent then drives color budget, dither, fal-video domain, and loop emphasis.

| Intent | Detection cues | Color budget | Dither | Loop emphasis |
|---|---|---|---|---|
| **loader** | "loader", "spinner", "loading icon", "progress GIF", "loading animation" | 16–32 | bayer | Critical — start ≈ end |
| **micro-animation** | "button hover", "icon animation", "small UI motion", "checkmark animation", "toast animation" | 16–32 | bayer | Critical |
| **hero** | "hero gif", "landing page", "homepage banner", "marketing gif", "feature gif" | 64 | bayer | Optional |
| **decorative** | "ambient loop", "atmosphere", "background motion", "decorative loop", "vibe gif" | 32–64 | bayer | Recommended |
| **photographic** | "cinematic gif", "realistic motion", "natural motion", "footage-style gif", "documentary gif" | 128 | floyd_steinberg | Rare |

### Intent → loop seam impact

- **loader / micro-animation** — loop is critical. Start frame ≈ end frame is mandatory. Brief-constructor injects "cyclical motion preferred, start frame visually equivalent to end frame" into the override notes.
- **decorative** — loop recommended. Drift-and-return or pulse-cycle motion preferred.
- **hero** — loop optional. Can be one-shot or looping; user intent decides.
- **photographic** — loop rare. These are typically narrative beats, not seamless loops.

### Intent → color budget rationale

- **16–32 colors** for flat art / line art / UI feedback — clean silhouettes, high contrast, banding is invisible on simple shapes. File size stays tiny.
- **64 colors** (default) — generic mixed content; works for most heroes and decoratives.
- **128 colors** for photographic — needed to avoid posterization on skin tones, gradients, sky transitions. File size grows but still manageable at 480px.

### Intent → dither rationale

- **bayer** (bayer_scale=5) — ordered dithering. Fast, predictable, low file size. Ideal for flat / illustrated / UI content. Can show its grid pattern on smooth gradients.
- **floyd_steinberg** — error-diffusion dithering. Smoother on photographic content (gradients, skin, sky). Larger file size; no visible grid.

---

## fal-video domain mapping per intent

When gif-maker spawns fal-video's brief-constructor, it must pick a fal-video domain. The mapping:

| Intent | fal-video domain | Rationale |
|---|---|---|
| **loader** | Abstract | Loaders are non-representational geometry / motion; Abstract domain's modifier library and locked-off + pulse-cycle defaults are ideal |
| **micro-animation** | Abstract | Same rationale as loader; UI micro-motion is geometric |
| **hero** | Cinema (subject-driven) or Product (object-driven) | Pick based on subject: a person/scene = Cinema; a single object = Product |
| **decorative** | Abstract (geometric/textural) or Landscape (atmospheric environmental) | Pick based on subject vocabulary: shapes/textures = Abstract; nature/environment = Landscape |
| **photographic** | Cinema (story/narrative beat) or Landscape (natural environment) | Pick based on whether there's a human/narrative subject (Cinema) or not (Landscape) |

> User can override the domain by phrasing the request to explicitly invoke a different one. ("Make me a portrait-style gif of a chef breathing slowly" → Portrait domain even though it's photographic intent.)

---

## Source-clip model per intent

| Intent | Default source model | When to opt into premium (Veo 3.1) |
|---|---|---|
| **loader** | Kling 2.5 Turbo Pro | Rarely — loaders don't need cinematic fidelity |
| **micro-animation** | Kling 2.5 Turbo Pro | Rarely |
| **hero** | Kling 2.5 Turbo Pro | When the user explicitly asks for premium photoreal motion |
| **decorative** | Kling 2.5 Turbo Pro | Rarely |
| **photographic** | Kling 2.5 Turbo Pro | When the user explicitly asks for cinematic realism — Veo's natural-light handheld is noticeably better here |

GIFs strip audio, so Veo's biggest feature (native audio) is wasted. Reserve Veo for the rare case where the visual fidelity jump is worth ~5× the cost.

---

## Worked examples — intent classification

| User request | Intent | fal-video domain | Color budget | Dither |
|---|---|---|---|---|
| "make me a loading spinner gif for my dashboard" | loader | Abstract | 16 | bayer |
| "small animated checkmark gif for a confirmation toast" | micro-animation | Abstract | 16 | bayer |
| "hero gif of headphones rotating for the homepage" | hero (object) | Product | 64 | bayer |
| "hero gif of a barista pulling espresso for the homepage" | hero (subject) | Cinema | 64 | bayer |
| "decorative gif of slow-drifting fog for a section background" | decorative | Landscape | 32 | bayer |
| "decorative gif of voronoi cells pulsing in deep navy" | decorative | Abstract | 32 | bayer |
| "cinematic gif of waves crashing on a basalt shore" | photographic | Landscape | 128 | floyd_steinberg |
| "photographic gif of a chef pouring olive oil in slow contemplation" | photographic | Cinema | 128 | floyd_steinberg |

---

## When intent is unclear

If the user's request doesn't match any single intent cluster cleanly, ask **one** disambiguation MCQ:

```
What kind of GIF is this for?
   a) Loader / spinner / progress indicator (small, looping, flat)
   b) Hero / landing-page motion (medium-rich, looping or one-shot)
   c) Decorative / ambient loop (background motion, looping)
   d) Photographic / cinematic (rich color, natural motion)
```

After the user picks, proceed with the matching intent's parameters. No follow-up MCQ — gif-maker is intentionally low-MCQ.

---

## What happens after classification

Intent classification feeds directly into:
1. **Color budget + dither** — passed to ffmpeg pipeline (`references/ffmpeg-commands.md`)
2. **fal-video domain** — passed to fal-video's brief-constructor as the `detected domain` input
3. **Loop emphasis** — folded into the override-notes block (`references/source-clip-spec.md`)
4. **Refinement suggestions reported to the user** — "want it shorter / wider / fewer colors / different dither?" tuned to intent
