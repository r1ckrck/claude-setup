# Outputs — fal-image

How fal-image names files, organizes folders, and writes JSON sidecars. Operational rules used by the SKILL.md orchestrator post-call.

---

## Project root

**CWD only.** Whatever folder Claude is open in is "the project." No detection logic, no walk-up-the-tree. If `$PWD` is `~/somewhere/X`, outputs land in `X/generated/`.

If `$PWD` is `$HOME`, `/`, `/etc`, `/usr`, `/var`, or any system path: **warn the user** and offer fallback `~/Documents/vizkit-outputs/<date>/...`. Do not silently pollute system folders.

---

## Folder layout

```
<cwd>/
└── generated/
    └── images/
        └── <YYYY-MM-DD>/
            ├── <slug>-vNN.<ext>
            └── <slug>-vNN.json
```

| Element | Rule |
|---|---|
| `generated/` | Created on first generation if missing |
| `images/` | Created on first image generation that day |
| Date folder | `YYYY-MM-DD`, local timezone. Created on first generation that day |

> fal-image writes only to `images/`. Other media types use sibling type folders (`videos/`, `gifs/`).

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
| "make me a hero image for a coffee shop website" | `coffee-shop-hero` |
| "logo for ember roastery" | `ember-roastery-logo` |
| "alpine ridge at sunrise" | `alpine-ridge-sunrise` |
| "edit this photo to remove the lamp post" | `remove-lamp-post` |
| "infographic showing Q4 revenue by region" | `q4-revenue-infographic` |
| "v01 of just generate something nice" | `untitled` (after stripping `v01` and filler) |

---

## Version increment

`-v01`, `-v02`, `-v03` — two-digit minimum, lowercase `v`, dash separator.

**Increment rule:** per slug, per date folder.

- If `coffee-shop-hero-v01.png` already exists in today's `images/2026-04-25/`, next save is `-v02`.
- Tomorrow's `images/2026-04-26/` starts fresh at `-v01` for the same slug.
- **Past `v99`:** format expands to `v100`, `v101`, etc. No zero-padding truncation. No rollover.

---

## JSON sidecar schema

Every generated image has a same-named `.json` sidecar with full reproduction info.

### Schema

```json
{
  "request": "string — verbatim user message",
  "slug": "string — derived slug",
  "version": "integer — version number (1, 2, 3…)",
  "type": "image",
  "domain": "cinema | product | portrait | editorial | ui | logo | landscape | abstract | infographic",
  "skill": "fal-image",
  "model": "string — fal model id used",
  "prompt": "string — the constructed prompt sent to fal (brief-constructor's output)",
  "params": {
    "aspect_ratio": "string",
    "resolution": "WIDTHxHEIGHT",
    "seed": "integer | null",
    "mode": "generate | edit | upscale | batch",
    "model_choice_reason": "string — one-line explanation of why this model was chosen",
    "reference_images": "array of {path_or_url, role} — empty when no references were passed; role is one of style | character | composition | edit-target",
    "preflight_confirmed": "boolean — true if the pre-flight summary was shown and the user confirmed",
    "domain_inferred": "boolean — true if domain was fallback-inferred from closest match",
    "request_id": "string — fal MCP request_id, the recovery handle if a call rejects/times out",
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
| `type` | Always `"image"` for fal-image |
| `domain` | Detected domain. Set `params.domain_inferred: true` if it was a fallback closest-match |
| `skill` | Always `"fal-image"` |
| `model` | The fal model id verbatim |
| `prompt` | The brief-constructor's output, post-strip |
| `params` | Open object — all model params and mode metadata land here |
| `preset` | Absolute path to the preset markdown used; null only if no preset matched |
| `cost_usd` | From fal MCP response. Two decimals enough |
| `timestamp` | ISO 8601 with timezone offset (e.g., `2026-04-25T11:42:18+05:30`), not `Z` |
| `duration_ms` | Wall-clock from MCQ-completion to file-write completion |
| `output_path` | Relative from project root, portable across machines |

### Worked example

```json
{
  "request": "make me a hero image for a coffee shop website",
  "slug": "coffee-shop-hero",
  "version": 1,
  "type": "image",
  "domain": "product",
  "skill": "fal-image",
  "model": "fal-ai/nano-banana-pro",
  "prompt": "A weathered ceramic espresso mug with a hairline chip at the rim, single shot of single-origin espresso showing a marbled tiger-stripe crema, resting on a worn oak counter inside a small-batch roastery at mid-morning...",
  "params": {
    "aspect_ratio": "4:3",
    "resolution": "1536x1152",
    "seed": null,
    "mode": "generate",
    "model_choice_reason": "Nano Banana Pro for premium photoreal hero with world-knowledge prompt",
    "reference_images": [],
    "preflight_confirmed": true,
    "domain_inferred": false,
    "request_id": "019dca..."
  },
  "preset": "/Users/<user>/Documents/Projects/<project>/.claude/skills/fal-image/presets/product.preset.md",
  "cost_usd": 0.05,
  "timestamp": "2026-04-25T11:42:18+05:30",
  "duration_ms": 4128,
  "output_path": "generated/images/2026-04-25/coffee-shop-hero-v01.png"
}
```

---

## Write order and atomicity

Per generation:

1. **Compute slug + version** by scanning `<cwd>/generated/images/<date>/`.
2. **mkdir -p** the date folder if missing.
3. **Save image bytes** to `<slug>-vNN.<ext>` first.
4. **Write JSON sidecar** at `<slug>-vNN.json`.
5. **Verify** both files exist with non-zero size.

### Failure modes

| Scenario | Behavior |
|---|---|
| fal call fails (timeout, content-policy, auth) | Report error to user. No files written. |
| fal succeeds, image download incomplete | Detect short-write, delete partial, report failure. |
| Image written, sidecar write fails | **Do not delete image** — user paid for it. **Echo the full sidecar JSON to chat as fallback log** so user has reproduction info. |
| Sidecar written, image write fails | Delete sidecar (orphan record), report failure. |

> The chat-output-as-fallback for sidecar failure is the safety net. Always echo full reproduction info to chat when a sidecar can't be written, even if the image saved successfully.

---

## Overwrite policy

Never overwrite an existing file. Increment version instead.

If a user explicitly asks to overwrite (e.g., `"replace coffee-shop-hero-v01"`), confirm in chat first, then overwrite. Default behavior is always increment.
