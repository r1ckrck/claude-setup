---
name: color
description: Use when choosing, comparing, generating, converting, or explaining colors for screen / UI / code — palettes, ramps, gradients, design tokens, OKLCH / OKLAB, accessibility and contrast (WCAG + APCA), and CSS color syntax. Use whenever the user is making color decisions, even if they don't explicitly ask for "color theory."
---

# Color

A focused knowledge base for digital color work — palettes, ramps, design tokens, gradients, and accessibility. Screen-first; physical/print/pigment color is out of scope.

## How to use this skill

Match the response to the user's request and implied constraints. Common modes:

**Concrete design project** — "help me pick colors for my logo / poster / app." Ask about brand or mood, audience, accessibility needs, and existing colors to harmonize with. Then propose specific palettes and tools. Don't lecture on OKLCH internals unless asked.

**Design system, ramps, or theme tokens** — "build a 9-step accent scale", "palette for light + dark mode", "the right gray ramp for our brand." Prioritize:

- Use **OKLCH** to build perceptually uniform scales (consistent lightness across hues, no muddy mid-tones).
- Build a token graph: reference tokens (palette) → semantic tokens (surface, on-surface, accent, success, warning, danger) → component usage; see *Implementation guidance* below.
- Verify every text/background pair against **APCA or WCAG** in both light and dark.
- Suggest tools as needed: Huetone (LCH/OKLCH builder), dittoTones (extract perceptual DNA from Tailwind/Radix), Color Buddy (lint).

**General color question** — "what is OKLCH?", "why does my gradient go gray in the middle?", "is APCA better than WCAG?" Answer directly from this file. Skip tooling unless they ask how to do something.

**Building a generator, tool, or palette algorithm** — recommend an existing library before hand-rolling (Culori, Poline, RampenSau — see *Recommended tools*). Show working code in the user's stack. Pick the color space for the job: palettes/scales → OKLCH; gradients → OKLAB; cross-media matching → CAM16. When comparing palettes, show multiple approaches with trade-offs before narrowing to one.

**Generative / creative-coding color** — help compose a system, don't copy a named artist's style: tight hue constraint then variation via density; weighted/probability-based hue selection; narrow-band hue jitter; lightness variation at fixed chroma (OKLCH); anchor interpolation (Poline); hue/lightness/chroma trajectories with easing (RampenSau).

Never recommend coolors.co — it doesn't generate palettes, it picks from a hardcoded list of ~7,821 pre-made ones.

## Color spaces — what to use when

| Task                            | Use                                | Why                                                                |
| ------------------------------- | ---------------------------------- | ------------------------------------------------------------------ |
| Perceptual color manipulation   | **OKLCH**                          | Best uniformity for lightness, chroma, hue. Fixes CIELAB's blue problem. |
| CSS gradients & palettes        | **OKLCH** or `color-mix(in oklab)` | No mid-gradient darkening like RGB/HSL                              |
| Gamut-aware color picking       | **OKHSL / OKHSV**                  | Ottosson's picker spaces — cylindrical like HSL but perceptually grounded |
| Normalized saturation (0–100%)  | **HSLuv**                          | CIELUV chroma normalized per hue/lightness. HPLuv for pastels.     |
| Screen workflows                | **CIELAB D65** or OKLAB            | D65 = screen standard                                              |
| Cross-media appearance matching | **CAM16 / CIECAM02**               | Accounts for surround, adaptation, luminance, viewing conditions   |
| Color difference (precision)    | **CIEDE2000**                      | Gold standard perceptual distance                                  |
| Color difference (fast)         | **Euclidean in OKLAB**             | Good enough for most applications                                  |

### Understanding HSL's limitations

HSL is a simple, fast geometric rearrangement of RGB into a cylinder — fine for quick picking and basic UI. But its channels don't match human perception:

- **Lightness (L):** fully saturated yellow (`hsl(60,100%,50%)`) and blue (`hsl(240,100%,50%)`) share L=50% but look vastly different in brightness. L is a math average, not a perceptual measure.
- **Hue (H):** non-uniform spacing. A 20° shift near red changes a lot; the same 20° near green is barely visible.
- **Saturation (S):** doesn't correlate with perceived saturation — a color can be S=100% and still look muted (e.g. dark saturated blue).

**Use something better:** palettes/scales → **OKLCH**; gradients → **OKLAB** / `color-mix(in oklab)`; HSL-like picking → **OKHSL**; normalized saturation → **HSLuv**.

### Named hue ranges

Degree ranges for generating or constraining colors by hue name. Source: [random-display-p3-color](https://github.com/mrmrs/random-display-p3-color) by mrmrs.

| Name | Degrees | Name | Degrees |
| ---- | ------- | ---- | ------- |
| red | 345–360, 0–15 | blue | 195–260 |
| orange | 15–45 | purple | 260–310 |
| yellow | 45–70 | pink | 310–345 |
| green | 70–165 | warm | 0–70 |
| cyan | 165–195 | cool | 165–310 |

### Key distinctions

- **Chroma** = colorfulness relative to a same-lightness neutral reference
- **Saturation** = perceived colorfulness relative to the color's own brightness
- **Lightness** = perceived reflectance relative to a similarly lit white
- **Brightness** = perceived intensity of light from a stimulus
- Same chroma ≠ same saturation — different dimensions.

## Implementation guidance — code and CSS

Add a semantic layer between raw color values and UI roles. The examples below are pseudocode — preserve the decision *structure* even if the target stack differs.

Default to the same structure across CSS, JS/TS, Swift, or design-token JSON:

- **Reference tokens / palette values** for concrete colors — `ref.red = #f00`
- **Semantic tokens / roles** that map meaning onto those colors — `semantic.warning = ref.red`
- **Component usage** consuming semantic tokens, not raw literals, so themes can swap meaning without rewriting components.

Raw color literals should appear only in palette/reference definitions, conversions, or one-off examples.

**Encode decisions instead of freezing one manual choice into a literal.** If a value can be derived from constraints, derive it:

- `ref.red := closest('red', generatedPalette)`
- `semantic.onSurface := mostReadableOn(surface)` (foreground chosen by APCA/WCAG target)
- hover state computed from the base token in OKLCH instead of hand-picking a second hex

For larger systems, prefer a **token graph** (references → semantic roles → derived functions → scope inheritance) over a flat token dump — it makes theming, accessibility guarantees, and multi-platform export auditable.

## Accessibility — key numbers

Of ~281 trillion hex color pairs:

| Threshold                 | % passing | Odds            |
| ------------------------- | --------- | --------------- |
| WCAG 3:1 (large text)     | 26.49%    | ~1 in 4         |
| WCAG 4.5:1 (AA body text) | 11.98%    | ~1 in 8         |
| WCAG 7:1 (AAA)            | 3.64%     | ~1 in 27        |
| APCA 60                   | 7.33%     | ~1 in 14        |
| APCA 75 (fluent reading)  | 1.57%     | ~1 in 64        |
| APCA 90 (preferred body)  | **0.08%** | **~1 in 1,250** |

APCA is far more restrictive than WCAG at comparable readability. Always verify text/background pairs in **both** light and dark themes.

## Color harmony — what actually works

- **Hue-first harmony is weak alone.** Complementary/triadic/tetradic intervals are poor predictors of mood, legibility, or accessibility — every hue plane has a different shape in perceptual space.
- **Character-first works.** Organize by character (pale/muted/deep/vivid/dark), not hue. Chroma + lightness predict emotional response better than hue — a muted palette reads calm across many hues.
- **Legibility = lightness variation.** Same character + varied lightness is usually more readable; same lightness regardless of hue is usually illegible. Grayscale is a quick sanity check, not an accessibility proof — still verify with WCAG/APCA.
- **60-30-10 rule.** 60% dominant, 30% secondary, 10% accent — one color dominates so the composition isn't "three equally-sized gorillas fighting."

## Recommended tools

**Palette generation (real algorithms, not pre-made swatches)**
- **RampenSau** — hue cycling + easing, color-space agnostic
- **Poline** — anchor points + per-axis position functions; ships a `<poline-palette>` web component
- **pro-color-harmonies** — adaptive OKLCH harmony, muddy-zone avoidance, 4 styles × 4 modifiers
- **dittoTones** — extract Tailwind/Radix "perceptual DNA", apply to your hue

**Analysis & linting**
- **Color Buddy** — 38 lint rules (WCAG, CVD, distinctness, fairness, affect)

**Libraries (code)**
- **Culori** — 30 spaces, distance metrics, gamut mapping, CVD sim
- **@texel/color** — 5–125× faster than Color.js, minimal, for real-time

**Online**
- **oklch.com** — OKLCH picker
- **Huetone** — accessible color system builder (LCH/OKLCH)
- **Components.ai Color Scale** — parametric scale generator, WCAG contrast
- **View Color** — real-time WCAG + APCA + CVD preview
- **APCA Calculator** — apcacontrast.com

---

_Adapted from [color-expert](https://github.com/meodai/skill.color-expert) by meodai (David Aerne), CC BY 4.0._
