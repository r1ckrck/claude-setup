# Source-Clip Spec — gif-maker

What gif-maker requests from fal-video and how it phrases the GIF-aware constraints. The most operationally-important reference — gif-maker reads this to know exactly what to inject into fal-video's brief-constructor.

---

## Source-clip request defaults (locked)

gif-maker passes these to the fal MCP video-generation tool unless the user overrides.

| Parameter | Default | Rationale |
|---|---|---|
| **Model** | `fal-ai/kling-video/v2.5-turbo/pro/text-to-video` (or `.../image-to-video` when a source still is provided) | Cheap workhorse at ~$0.07/s. Quality is more than sufficient for color-reduced GIF output, and motion fidelity beats older models comfortably. User can opt into Veo 3.1 (`fal-ai/veo3.1`) when premium photoreal motion is worth the cost jump (~5×). |
| **Duration** | Model minimum (5s on Kling 2.5 Turbo Pro) | Can't request shorter than the model's floor. If user wants ≤3s, trim locally with ffmpeg `-t` (see "Trimming for short GIFs" below). fps doesn't affect cost — only seconds do. |
| **Resolution** | Smallest tier the chosen model exposes | The GIF will be scaled to 480px wide anyway. Lower source resolution = cheaper without quality loss for the final output. |
| **Audio** | Always **off** | Irrelevant for GIF. Saves any audio surcharge on capable models. |
| **Aspect ratio** | Per user intent | Square for buttons / loaders · 16:9 for hero · vertical for stories. |
| **fps** | Accept native | fps is not controllable on most fal models. Whatever the model outputs (~24–30fps) gets downsampled with ffmpeg to GIF target fps (10 default). |

> **Submission:** use `submit_job` + `check_job` polling, never `run_model`. Video generation runs 30–90s and the sync pattern times out unreliably. Pattern + recovery in `references/fal-mcp-flow.md`.

### Source-clip overrides users can request

- **Model** — "use Veo for this hero gif" → swap the model param to `fal-ai/veo3.1`. Cost goes up substantially; the pre-flight summary surfaces it before submission.
- **Duration** — "make it 3 seconds" → set duration=3 if the model accepts it; otherwise use model min and trim with ffmpeg post-fal.
- **Aspect ratio** — "vertical" / "16:9" / "square" → set the aspect_ratio param.

### Locked-out: things users cannot override

- **Audio** — always off. GIFs strip audio anyway, and audio surcharges on capable models add cost for nothing.
- **Source resolution** — always smallest tier. Higher res wastes money since GIF gets downsized to 480px anyway.

---

## GIF-aware override-notes pattern

When gif-maker spawns fal-video's brief-constructor, it passes constraints into the brief-constructor's `custom override notes` field (one of the 11 inputs in fal-video's input contract). This is how GIF-specific concerns reach the prompt without rewriting the user's request.

### Template

```
This clip is for a GIF output. Apply these constraints during prompt construction:

1. Color budget: <color budget band per intent — e.g., "16-32 colors target">.
   Bias the scene toward <descriptive guidance — e.g., "limited palette, high-contrast silhouettes, clean flat shapes">.

2. Scene simplicity: cleaner background, fewer distinct subjects, clear silhouettes.
   GIF compression rewards simplicity at the pixel level.

3. Looping: <if loop-friendly intent>
   Start frame should be visually equivalent to end frame. Cyclical motion preferred (drift-and-return,
   pulse-cycle, breath-cycle). Subject motion intensity should be still or subtle.

4. Duration: <target duration in seconds>. Lean shorter. Simple motion that completes within the clip
   — no narrative beats that need more than the duration to read.

5. Aspect ratio: <user-intent aspect ratio>.
```

### Substitution table per intent

| Intent | Color budget phrasing | Loop phrasing | Notes |
|---|---|---|---|
| **loader** | "16-32 colors target — bias toward limited palette, high-contrast silhouettes, clean flat shapes" | Loop critical — start frame ≈ end frame, cyclical motion | Subject motion intensity should be still or subtle |
| **micro-animation** | "16-32 colors target — limited palette, single-stroke or filled shapes" | Loop critical | Subject motion intensity subtle |
| **hero** | "64 colors target — moderate palette range, can include gradient transitions" | Loop optional | Subject motion intensity per request |
| **decorative** | "32-64 colors target — moderate palette, atmospheric textures acceptable" | Loop recommended | Drift-and-return motion ideal |
| **photographic** | "128 colors target — full palette range for skin tones, gradients, sky transitions" | Loop rare | Photographic content = narrative beats, not seamless loops |

> **Critical:** color count is *not* a literal prompt instruction. The brief-constructor reasons about it from the override notes and reflects it through aesthetic choices ("limited palette", "high-contrast silhouettes", "atmospheric textures"), not by writing "use exactly 16 colors" into the fal prompt.

---

## fps handling

Accept whatever fal's model produces natively (~24–30fps). **Always downsample with ffmpeg to GIF target fps.** No fal model supports 10fps output natively, and fps doesn't affect per-second pricing — so there is no upstream lever.

The fps target gets passed to the brief-constructor as `target fps = accept native — fps not controllable on most fal models`. The brief-constructor then leaves fps out of the prompt entirely (it's a post-processing concern).

---

## Trimming for short GIFs (≤3s)

If user asks for a GIF shorter than the source-clip duration:

1. Generate the source clip at the model's minimum duration (~5s).
2. Apply ffmpeg `-t <seconds>` during the palette/paletteuse pipeline to trim to the target.

See `references/ffmpeg-commands.md` for the trim variant of the two-pass pipeline.

The full-length source MP4 stays in `_source/` so the user can re-encode at a different trim length later without paying for another fal generation.

> **Never re-request shorter from fal** — model min is a floor. Asking for 2s when the floor is 5s either fails or returns 5s anyway.

---

## Worked example — full request flow

User request: *"make me a loading spinner gif for my dashboard"*

### Step 1 — gif-maker classifies intent

Intent: **loader** (per `references/strategy.md`).

Parameters resolved:
- Color budget: 16-32 colors
- Dither: bayer
- fal-video domain: Abstract
- Loop emphasis: critical
- Aspect ratio: square (default for loaders, but inferred from "loading spinner" cue)

### Step 2 — gif-maker builds the override-notes block

```
This clip is for a GIF output. Apply these constraints during prompt construction:

1. Color budget: 16-32 colors target — bias toward limited palette, high-contrast silhouettes, clean flat shapes.

2. Scene simplicity: cleaner background, fewer distinct subjects, clear silhouettes. GIF compression rewards simplicity at the pixel level.

3. Looping: Start frame should be visually equivalent to end frame. Cyclical motion preferred (drift-and-return, pulse-cycle, breath-cycle). Subject motion intensity should be still or subtle.

4. Duration: 5s (model minimum). Lean shorter. Simple motion that completes within the clip.

5. Aspect ratio: 1:1 (square).
```

### Step 3 — gif-maker spawns fal-video's brief-constructor

Inputs passed to the subagent:
- skill-root: `<absolute path to>/.claude/skills/fal-video`
- user request: "make me a loading spinner gif for my dashboard"
- detected domain: **abstract**
- preset path: `<absolute path to>/.claude/skills/fal-video/presets/abstract.preset.md`
- mode: generate
- MCQ answers: none
- custom override notes: *(the block above)*
- target duration: 5
- target fps: accept native

### Step 4 — brief-constructor returns a prompt

Example output (~140 words):

> A field of small geometric arcs in deep navy on a clean cream background, single concentric ring rotating slowly clockwise as it pulses outward and contracts back on a four-second pulse-cycle, creating a seamless loop where the start frame matches the end frame exactly. Limited palette of three colors — deep navy, cream, single brass accent — with high-contrast silhouettes and clean flat shapes. Locked-off frame, breath-cycle pacing, subject motion subtle. Background remains a single solid cream surface throughout, no atmospheric noise or gradient transitions, clean compositional negative space. Generative motion register evoking Casey Reas, op-art bilateral symmetry, Bauhaus geometric register translated to motion. Suitable for a dashboard loader at small display size.

### Step 5 — gif-maker calls fal MCP

Model: `fal-ai/kling-video/v2.5-turbo/pro/text-to-video`
Aspect ratio: 1:1
Resolution: smallest tier
Audio: off
Duration: 5s
Prompt: *(brief-constructor's output)*

### Step 6 — gif-maker saves source MP4 + runs ffmpeg

Source saved to `generated/gifs/2026-04-26/dashboard-loader-spinner-v01-source.mp4` in `_source/` subdir.

ffmpeg pipeline runs with:
- fps=10
- width=480
- max_colors=16
- dither=bayer

(See `references/ffmpeg-commands.md` for the exact two-pass commands.)

### Step 7 — gif-maker writes GIF + sidecar

Output: `generated/gifs/2026-04-26/dashboard-loader-spinner-v01.gif` + `.json` sidecar.

Cost reported: **~$0.35** (Kling 2.5 Turbo Pro at 5s) + $0 ffmpeg.

Refinement suggestion offered: *"want it tinier (320px) or with even fewer colors (8)?"*
