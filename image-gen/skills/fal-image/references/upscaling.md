# Upscaling — fal-image

The upscale flow: take an existing image and produce a higher-resolution version. Routes here when the user has a source image and asks for it bigger / sharper / higher-res.

---

## When to use

- User provides a source image AND asks to increase its resolution or sharpness
- Trigger phrases: "upscale this", "make this higher resolution", "improve the quality of this", "2x this image", "enhance this", "make this bigger", "print-quality this"

If the user wants to *generate* at a higher resolution rather than upscale an existing image, that's text-to-image with the resolution param — not the upscale flow.

---

## Source-image handling

Same as edit flow:

| Source format | How to handle |
|---|---|
| **Local file path** | Upload via fal MCP file-upload tool (runtime-discover). Get back a CDN URL. |
| **URL** | Pass directly. |

---

## Upscaler call

The orchestrator picks a fal upscaler model at runtime. Use `ToolSearch` or the fal MCP's model-listing tool to find available upscalers (e.g., clarity-upscaler, esrgan, real-esrgan variants — names change, do not hardcode).

### Parameters typically exposed

| Param | Default behavior |
|---|---|
| **Scale factor** | `2x` is the safe default. `4x` available on most upscalers but cost grows ≥linearly. Ask the user only if they don't specify. |
| **Style preservation** | Most upscalers offer "preserve" vs "creative" modes. Default to **preserve** — keep the original aesthetic intact. |
| **Detail enhancement** | Some upscalers add detail at high frequency. Default to subtle, not aggressive — avoids hallucinated artifacts. |

### No prompt construction needed

Unlike text-to-image and edit, upscaling typically does not take a prompt. The brief-constructor is **bypassed** for upscale — the orchestrator calls the upscaler tool directly with the source URL + scale + preservation flag.

If the upscaler does accept an optional prompt (some do — for guided upscaling), the orchestrator can pass a one-line description of the source content to anchor the model. Brief-constructor is overkill for this; the orchestrator can compose inline.

---

## Output naming

| Source | Output slug |
|---|---|
| Upscaling a previously generated VizKit image (sidecar exists with a known slug) | `<source-slug>-upscaled-v01.png` |
| Upscaling an arbitrary image with no known slug | `upscale-<short-hash>-v01.png` where `short-hash` is a 6-char hash of the source path |
| User explicitly named the output | Use that name |

JSON sidecar `mode: "upscale"`, `params.scale_factor: <2 | 4 | etc.>`, `params.source_image: "<original-path-or-url>"`.

---

## Cost note

Upscalers vary widely in cost. 4x upscaling can cost ≥10× a base image generation. Always surface cost in the pre-flight summary for upscale requests. If user says "just go ahead," still log the cost in the sidecar — they should know what they paid.

---

## Limitations

- Upscalers cannot recover detail that wasn't in the source. They invent plausible detail; the result is "high-resolution-looking" not "true high-resolution."
- Aggressive enhancement can hallucinate artifacts (extra fingers, hair tendrils, false text). Use preserve mode by default.
- Upscaling text-heavy images often corrupts the text. For text-heavy hero images, regenerate at higher resolution from scratch instead.
- Maximum supported source resolution varies per upscaler — check at runtime before sending a 4K source to a 2x upscaler that expects ≤1024px input.
