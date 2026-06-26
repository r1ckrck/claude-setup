# Editing — fal-image

The image-edit flow: take an existing image and modify it. Routes here when the user provides a source image and asks to change something about it.

---

## When to use

- User provides a local image file path or URL AND asks to modify it
- Trigger phrases: "edit this image", "modify this photo", "change the background", "remove the X from this", "restyle this", "swap X for Y", "make this darker / brighter / cleaner", "fix the lighting in this"

If the user wants to *generate fresh* something inspired by an existing image (not edit it), that's text-to-image with a style reference, not the edit flow.

---

## Picking the right edit model

Different edit shapes call for different models. The orchestrator picks based on the request:

| Edit shape | Model | Why |
|---|---|---|
| **Single-reference conversational edit** ("change the jacket to red", "remove the sign", "swap the background for a beach") | **Flux Kontext [pro]** | Workhorse single-reference edit at $0.04. Targeted local changes, fast, predictable. Name subjects explicitly — no pronouns. |
| **Multi-reference fusion / character consistency** ("use this person from image 1 in the setting from image 2", "generate four shots of this character in different scenes") | **Nano Banana Pro /edit** or **Flux 2 [flex] /edit** | Native multi-image input. Nano Banana Pro accepts up to 14 references; Flux 2 [flex] uses the indexed `@image1` syntax for designer-grade compositional control. |
| **Premium / iterative editing with world knowledge** (long conversational sessions, brand integration, complex spatial reasoning) | **Nano Banana Pro /edit** | Highest fidelity. 4 variants per call. Masks-free. |
| **Text-heavy in-image edits** (signage, multilingual labels, UI text) | **Qwen Image Edit** | Specialist for in-image text editing — beats Flux Kontext for typography-driven edits. |

The brief-constructor receives the chosen model as `target_model` and adapts its prompt phrasing.

---

## Source-image handling

The source image must reach fal as a URL. Two paths:

| Source format | How to handle |
|---|---|
| **Local file path** (e.g., `~/Documents/photo.jpg`, `./hero.png`) | Upload via the direct fal REST API — `POST https://rest.alpha.fal.ai/storage/upload/initiate` returns `{upload_url, file_url}`, then `PUT <upload_url>` with the file body. Use the returned `file_url` as the model's image input. fal MCP's `upload_file` tool's `file_path` param fails on HTTP-transport MCPs (the standard Claude Code setup). |
| **Already a URL** (e.g., from clipboard, web page, prior fal generation) | Pass directly to the model. No upload needed. |

**Auth gotcha:** fal MCP wants `Authorization: Bearer <key>`. fal REST wants `Authorization: Key <key>`. Different prefixes for the same key.

---

## Reference-image roles

When one or more images come in alongside the request, each carries a role inferred from the user's phrasing:

| Phrasing pattern | Inferred role |
|---|---|
| "change X in this" / "remove Y" / "swap A for B" | **edit-target** — the canvas being modified |
| "in the style of this" / "matching this look" / "make it feel like this" | **style** — match palette, register, lighting |
| "this person across these scenes" / "use this character" / "preserve their face" | **character** — identity lock |
| "match this layout" / "same framing as this" / "use this composition" | **composition** — pose / framing reference |

Multiple references with mixed roles are normal — Nano Banana Pro and Flux 2 [flex] handle them in a single call.

---

## Edit-prompt construction

The brief-constructor adapts its formula slightly for edit mode:

| Slot | For edit mode |
|---|---|
| **Subject** | The element being modified ("the lamp post in the upper-left", "the background sky", "the sweater the subject is wearing") |
| **Action** | The modification verb ("remove", "replace with", "make darker", "extend", "swap for") |
| **Location/Context** | What to preserve unchanged ("keep all other elements identical", "preserve the figure's pose and lighting") |
| **Composition** | Frame and crop preserved unless the edit explicitly changes it |
| **Style + Lighting** | Match existing image's register — same color grading, same light direction, same film-stock feel. Critical: **do not introduce a new register**. |

### Key edit-prompt rules

- **Edge preservation language**: "preserve sharp edges where the original is sharp", "match grain and noise", "blend seamlessly at the boundary"
- **Color consistency anchors**: "match the existing color temperature and saturation", "preserve the warm amber-magenta highlights from the source"
- **Lighting consistency**: "preserve the original light direction and shadow pattern"
- **Don't reword the whole image** — describe only the change. The edit model will preserve everything you don't mention.
- **Be specific about location**: "the lamp post in the upper-left third" beats "the lamp post"
- **Name subjects, never pronouns** (Flux Kontext fails on pronouns; safer everywhere)
- **Quote literal text edits**: `change the sign to read "OPEN 24"`

### Worked example

User: *"edit this photo to remove the lamp post"* + image at `./photo.jpg`

Constructed edit prompt:

> Remove the cast-iron lamp post standing in the upper-left third of the frame. Replace with seamless extension of the surrounding red-brick wall and overcast grey sky behind it. Preserve all other elements identically — the two figures walking, the wet cobblestone street, the soft directional light from camera-left. Match the existing slightly desaturated color grading, late-afternoon overcast light quality, and subtle film grain. Blend the patched area seamlessly with no visible boundary.

---

## Output naming

Edit outputs land in the same `generated/images/<date>/` folder as text-to-image generations.

| Source | Output slug |
|---|---|
| Edit verb is the dominant action | Slug derived from the verb + object: `remove-lamp-post-v01.png`, `change-background-v01.png` |
| User has a clear named subject in the request | `<subject>-edited-v01.png` |
| Source image has a known related slug (e.g., from prior generation) | `<source-slug>-edited-v01.png` |

JSON sidecar `mode: "edit"` and `params.reference_images` array records each input image's path/URL and inferred role.

---

## Side-by-side comparison

When the user wants to see before/after side-by-side, that's a downstream ffmpeg compositing step — fal-image returns the edited image and the original path, leaving the montage to the user's local toolchain.

---

## Limitations

- fal edit models cannot extend the canvas beyond the original frame (use outpainting models specifically when needed — different routing)
- Edit models work best on photo-realistic content. For illustrated/stylized edits, results vary
- Text changes within an image are most reliable on Qwen Image Edit; other models may corrupt surrounding text
- Removing a subject from a complex composition can leave artifacts; verify visually before declaring success
