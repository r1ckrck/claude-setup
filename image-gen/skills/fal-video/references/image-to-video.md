# Reference-image inputs — fal-video

How to pass an existing image into a fal video generation as a reference. Routes here when the user supplies a source image alongside their request — for any role: animating it, matching its style, locking a character's identity, or holding its composition.

---

## When this applies

- User provides a local image file path or URL alongside the video request
- Trigger phrases: "animate this image", "bring this to life", "make this move", "in the style of this", "use this character across these clips", "match this composition", "use the person from this image"

A request without any reference image is a pure text-to-video — handled by the main flow, not this file.

---

## Reference-image roles

The orchestrator infers the role from the user's phrasing. The brief-constructor uses the role to phrase the reference correctly into the prompt.

| User phrasing | Inferred role | Prompt language to use |
|---|---|---|
| "animate this", "bring this photo to life", "make this still move" | **animate-target** — the source frame to animate | "preserve the source frame's exact composition" |
| "in the style of this", "matching this look", "feel like this" | **style** — palette, lighting register, color temperature | "matching the lighting register and color temperature of the reference" |
| "use this character", "this person across these scenes", "preserve their face" | **character** — identity lock | "the subject from the reference, identity preserved across the clip" |
| "match this layout", "same framing as this" | **composition** — pose, framing, camera angle | "matching the framing and layout of the reference" |

Multiple references with mixed roles are common (e.g., one character + one style). Veo 3.1's "Ingredients to Video" accepts up to three reference images per call; Kling I2V accepts one.

---

## Source-image handling

The source image must reach fal as a URL. Two paths:

| Source format | How to handle |
|---|---|
| **Local file path** (e.g., `~/Documents/photo.jpg`, `./hero.png`) | Upload via the direct fal REST API — see "Local file upload" below. The MCP `upload_file` tool's `file_path` param fails on HTTP-transport MCPs (the standard Claude Code setup). |
| **Already a URL** (e.g., from clipboard, web page, prior fal generation) | Pass directly to the model. No upload needed. |

### Local file upload — direct fal REST

Two-step pattern:

1. **POST initiate** — `POST https://rest.alpha.fal.ai/storage/upload/initiate` with header `Authorization: Key <FAL_KEY>` and body `{"file_name": "<name>", "content_type": "<mime>"}`. Returns `{upload_url, file_url}`.
2. **PUT bytes** — `PUT <upload_url>` with the file body and matching `Content-Type` header.

Use the returned `file_url` as the model's reference input. Pass each role as a separate input parameter where the model schema supports it.

**Auth gotcha:** fal MCP wants `Authorization: Bearer <key>`. fal REST wants `Authorization: Key <key>`. Different prefixes for the same key. Wrong prefix returns a generic 401.

---

## Prompt construction with references

The brief-constructor's job is the prose; the orchestrator wires the reference inputs as separate API parameters. The prose **does not redescribe** the reference image's content — that defeats the purpose. Instead, it states the role:

| Role | Prose pattern |
|---|---|
| **animate-target** | Lead with motion: "Slow handheld push-in over four seconds. Preserve the source frame's exact composition, color temperature, and lighting direction. Subject motion subtle — only [specific small motion]. No new elements introduced." |
| **style** | "Matching the lighting register and color temperature of the reference. [Subject + action + motion description]." |
| **character** | "The subject from the reference, identity preserved across the clip — [continue with the action and motion brief]." |
| **composition** | "Matching the framing and layout of the reference — [continue with subject substitution and motion brief]." |

### When the role is animate-target (i2v specifically)

The source image already locks four of the six slots. The brief-constructor truly fills only **Motion + Action**:

| Slot | Handling |
|---|---|
| **Subject** | Source image — don't redescribe |
| **Action** | The new motion verb the user wants ("animate this", "make it spin", "have her turn her head") |
| **Location/Context** | Source image — don't redescribe |
| **Composition** | Source image — don't redescribe (camera framing comes from the still) |
| **Motion** | The dominant slot — camera move + pacing + subject motion intensity |
| **Style + Lighting** | Source image — match its existing register; do not introduce new lighting |

### Key animate-target rules

- **Edge / continuity language**: "preserve the source frame's exact composition", "match the existing lighting direction and color temperature", "no new elements introduced", "subject identity remains constant"
- **Motion-first opening**: "Slow push-in over four seconds with the subject..." rather than describing the subject
- **Subject-motion intensity is critical**: i2v models tend to over-animate stills. State explicitly: "subject motion subtle — only [specific small motion]" or "subject still — only camera moves" or "subject moderate — clear gestures"
- **Don't reword the whole image** — describe only what should move and how
- **Be specific about what moves**: "the steam wisp drifts upward and curls toward camera-left" beats "things move"

### Prompt length

- Target **50–120 words** for animate-target (shorter than T2V's 100–200)
- The source image carries most of the information; padding the prompt with re-description hurts more than helps
- For pure style or composition references on a T2V, target the standard 100–200 words — the prose still does most of the work since the reference is just a guide

---

## Worked example — animate-target

User: *"animate this product photo with a slow rotate"* + image at `./headphones.jpg`

Constructed prompt:

> Slow rotate of the source frame over four seconds, gentle drift pacing, subject motion still — only the camera or subject rotates on a vertical axis, while the lighting, surface, and shadow pattern remain identical to the source. Single specular highlight travels subtly across the brushed-aluminum coil as the rotation reveals the rear of the earcup. Preserve the source's exact composition, color temperature, and lighting direction. Match the existing soft directional key from camera-right with the white-card fill and the sharp drop-shadow falling away to the lower-left. No new elements introduced.

Length: ~95 words. Motion is the dominant clause. Preservation language is explicit.

---

## Output naming

Reference-driven outputs land in the same `generated/videos/<date>/` folder as text-to-video generations.

| Source | Output slug |
|---|---|
| Source image has a known related slug (e.g., from a prior generation with sidecar) | `<source-slug>-animated-vNN.mp4` for animate-target; `<source-slug>-styled-vNN.mp4` for style match |
| User has a clear named subject in the request | `animate-<subject>-vNN.mp4` |
| Source image is arbitrary (no known slug) | `animate-<short-hash>-vNN.mp4` where `short-hash` is a 6-char hash of the source path |

JSON sidecar `mode: "i2v"` for animate-target, otherwise `mode: "generate"` with the references captured in `params.reference_images` as `[{path_or_url, role}, ...]`.

---

## Limitations

- fal i2v models cannot extend the canvas beyond the source frame's aspect ratio. Different aspect ratio? Regenerate from text-to-video instead.
- Some i2v models work best on still-life / product / landscape sources; portrait i2v varies widely by model.
- Text within a source image often corrupts during animation — small text edits across frames produce flickering artifacts. For text-heavy sources, lock the camera move to "locked-off" and the subject motion to "still" to minimize the risk.
- i2v models tend to over-animate stills by default. Always state subject motion intensity explicitly.
- Some models cap the number of reference images (Veo 3.1 takes up to 3, Kling I2V takes 1). Check the model schema before passing more than one.
- Some models have a maximum input resolution; check at runtime before passing a 4K source.
