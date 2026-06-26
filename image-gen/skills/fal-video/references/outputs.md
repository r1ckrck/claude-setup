# Outputs — fal-video

How fal-video names files, organizes folders, and writes JSON sidecars. Operational rules used by the SKILL.md orchestrator post-call.

---

## Project root

**CWD only.** Whatever folder Claude is open in is "the project." No detection logic, no walk-up-the-tree. If `$PWD` is `~/somewhere/X`, outputs land in `X/generated/`.

If `$PWD` is `$HOME`, `/`, `/etc`, `/usr`, `/var`, or any system path: **warn the user** and offer fallback `~/Documents/vizkit-outputs/<date>/...`. Do not silently pollute system folders.

---

## Folder layout

```
<cwd>/
└── generated/
    └── videos/
        └── <YYYY-MM-DD>/
            ├── <slug>-vNN.mp4
            └── <slug>-vNN.json
```

| Element | Rule |
|---|---|
| `generated/` | Created on first generation if missing |
| `videos/` | Created on first video generation that day |
| Date folder | `YYYY-MM-DD`, local timezone. Created on first generation that day |

> fal-video writes only to `videos/`. Other media types use sibling type folders (`images/`, `gifs/`).

> Default extension is `.mp4` — most fal video models output mp4. If a model returns a different format (webm, mov), use whatever the model produced and reflect the actual extension in `output_path`.

---

## Slug derivation

Auto-derived from the user's request:

1. **Lowercase**
2. **Dash-separated** (no spaces, no underscores)
3. **Drop articles** — "a", "an", "the"
4. **Drop filler** — "of", "for", "with", "please", "can you", etc.
5. **Max 6 words** — pick the most descriptive nouns/adjectives, drop the rest
6. **Strip punctuation** — except hyphens already in proper nouns
7. **ASCII only** — transliterate accents (`ø` → `o`, `é` → `e`)
8. **No leading/trailing dashes**
9. **Strip explicit version tokens** from input — remove `v01`, `v02`, `version 1`, `v.2`, etc. before derivation
10. **Empty-slug fallback** — if the result is empty or under 3 characters, use the first 3 noun-like tokens from the formula's Subject slot. If still nothing usable, fall back to `untitled`.

### Examples

| Request | Slug |
|---|---|
| "make a hero video for a coffee shop website" | `coffee-shop-hero` |
| "spinning headphones video for the product page" | `headphones-spin` |
| "alpine ridge at sunrise time-lapse" | `alpine-ridge-sunrise` |
| "animate this product photo with a slow rotate" | `slow-rotate` (or source-derived if known: `headphones-animated`) |
| "moody portrait clip of a chef in a kitchen" | `chef-kitchen-portrait` |
| "abstract loop of voronoi cells pulsing" | `voronoi-cells-pulse` |
| "v01 of just generate something nice" | `untitled` (after stripping `v01` and filler) |

---

## Version increment

`-v01`, `-v02`, `-v03` — two-digit minimum, lowercase `v`, dash separator.

**Increment rule:** per slug, per date folder.

- If `coffee-shop-hero-v01.mp4` already exists in today's `videos/2026-04-26/`, next save is `-v02`.
- Tomorrow's `videos/2026-04-27/` starts fresh at `-v01` for the same slug.
- **Past `v99`:** format expands to `v100`, `v101`, etc. No zero-padding truncation. No rollover.

---

## JSON sidecar schema

Every generated video has a same-named `.json` sidecar with full reproduction info.

### Schema

```json
{
  "request": "string — verbatim user message",
  "slug": "string — derived slug",
  "version": "integer — version number (1, 2, 3…)",
  "type": "video",
  "domain": "cinema | product | portrait | editorial | landscape | abstract",
  "skill": "fal-video",
  "model": "string — fal model id used",
  "prompt": "string — the constructed prompt sent to fal (brief-constructor's output)",
  "params": {
    "aspect_ratio": "string",
    "resolution": "WIDTHxHEIGHT",
    "duration_seconds": "number — clip duration",
    "fps": "number — playback frame rate",
    "audio_enabled": "boolean — true when user opted into audio; default false",
    "audio_brief": "string — one-line audio brief passed to the model when audio_enabled is true; otherwise null",
    "mode": "generate | i2v | batch",
    "seed": "integer | null",
    "model_choice_reason": "string — one-line explanation of why this model was chosen",
    "reference_images": "array of {path_or_url, role} — empty when no references were passed; role is one of style | character | composition | animate-target",
    "preflight_confirmed": "boolean — true if the pre-flight summary was shown and the user confirmed",
    "domain_inferred": "boolean — true if domain was fallback-inferred from closest match",
    "motion_intensity": "still | subtle | moderate | active | vigorous",
    "request_id": "string — fal MCP request_id, the recovery handle if a call rejects/times out",
    "batch_index": "integer — only when mode=batch",
    "batch_total": "integer — only when mode=batch",
    "batch_rotation": "motion | style | composition | action | location — only when mode=batch",
    "...": "any other model-specific params used"
  },
  "preset": "string — absolute path to preset .md used, or null",
  "cost_usd": "number — what fal returned",
  "timestamp": "ISO 8601 string with timezone offset",
  "duration_ms": "integer — wall-clock for the operation",
  "output_path": "string — relative path from project root"
}
```

### Field rules

| Field | Notes |
|---|---|
| `request` | Verbatim user message |
| `slug` | Same as the slug used in the filename |
| `version` | Plain integer, not `"v02"` — filename has the `v` prefix |
| `type` | Always `"video"` for fal-video |
| `domain` | Detected domain. Set `params.domain_inferred: true` if it was a fallback closest-match |
| `skill` | Always `"fal-video"` |
| `model` | The fal model id verbatim |
| `prompt` | The brief-constructor's output, post-strip |
| `params.duration_seconds` | The actual clip duration (some models lock this; capture what fal returned) |
| `params.fps` | The actual playback fps |
| `params.audio_enabled` | Boolean; defaults to `false` unless the user explicitly requested audio. When `true`, `params.audio_brief` carries the one-line audio cue passed to the model. |
| `params.mode` | `"generate"`, `"i2v"`, or `"batch"` |
| `params.reference_images` | Array of `{path_or_url, role}` for any reference images. Empty array when no references were passed. For `mode: "i2v"`, the source still appears here with role `animate-target`. |
| `params.motion_intensity` | One of the 5 bands: still / subtle / moderate / active / vigorous |
| `params.batch_*` | Only present when `mode: "batch"` |
| `preset` | Absolute path to the preset markdown used; null only if no preset matched |
| `cost_usd` | From fal MCP response. Two decimals enough |
| `timestamp` | ISO 8601 with timezone offset (e.g., `2026-04-26T11:42:18+05:30`), not `Z` |
| `duration_ms` | Wall-clock from MCQ-completion to file-write completion |
| `output_path` | Relative from project root, portable across machines |

### Worked example — Cinema T2V

```json
{
  "request": "make a video of a barista pulling espresso at a small-batch roastery in the morning",
  "slug": "barista-espresso-roastery",
  "version": 1,
  "type": "video",
  "domain": "cinema",
  "skill": "fal-video",
  "model": "fal-ai/veo3.1",
  "prompt": "A 35-year-old barista with sleeves rolled up, pulling a shot of espresso at a small-batch roastery during golden hour, the brass espresso machine catching warm directional light from tall windows behind. Subject motion moderate — hands work the portafilter and tamp deliberately. Slow handheld push-in over five seconds, breath-held pacing, gentle parallax as the camera drifts toward the steam. Captured on ARRI Alexa Mini LF with 50mm Cooke S7/i at T2.0. Warm Rembrandt key from camera-left, late-analog 1990s film register, Roger Deakins cinematography.",
  "params": {
    "aspect_ratio": "4:3",
    "resolution": "1280x960",
    "duration_seconds": 5,
    "fps": 24,
    "audio_enabled": false,
    "audio_brief": null,
    "mode": "generate",
    "seed": null,
    "model_choice_reason": "Veo 3.1 for cinematic register and natural-light handheld realism",
    "reference_images": [],
    "preflight_confirmed": true,
    "domain_inferred": false,
    "motion_intensity": "moderate",
    "request_id": "019dca..."
  },
  "preset": "/Users/<user>/Documents/Projects/<project>/.claude/skills/fal-video/presets/cinema.preset.md",
  "cost_usd": 0.25,
  "timestamp": "2026-04-26T11:42:18+05:30",
  "duration_ms": 28412,
  "output_path": "generated/videos/2026-04-26/barista-espresso-roastery-v01.mp4"
}
```

---

## Write order and atomicity

Per generation:

1. **Compute slug + version** by scanning `<cwd>/generated/videos/<date>/`.
2. **mkdir -p** the date folder if missing.
3. **Save video bytes** to `<slug>-vNN.<ext>` first (where `<ext>` is whatever fal returned, default `.mp4`).
4. **Write JSON sidecar** at `<slug>-vNN.json`.
5. **Verify** both files exist with non-zero size.

### Failure modes

| Scenario | Behavior |
|---|---|
| fal call fails (timeout, content-policy, auth) | Report error to user. No files written. |
| fal succeeds, video download incomplete | Detect short-write, delete partial, report failure. |
| Video written, sidecar write fails | **Do not delete video** — user paid for it. **Echo the full sidecar JSON to chat as fallback log** so user has reproduction info. |
| Sidecar written, video write fails | Delete sidecar (orphan record), report failure. |

> The chat-output-as-fallback for sidecar failure is the safety net. Always echo full reproduction info to chat when a sidecar can't be written, even if the video saved successfully.

---

## Overwrite policy

Never overwrite an existing file. Increment version instead.

If a user explicitly asks to overwrite (e.g., `"replace coffee-shop-hero-v01"`), confirm in chat first, then overwrite. Default behavior is always increment.
