---
name: fal-image
description: Generate, edit, or upscale images via fal.ai. Triggers on natural-language requests like "generate an image", "create a logo / banner / hero / poster / icon", "make a visual of X", "design an image", "illustrate X", "edit this image", "modify this photo", "change the background of X", "restyle this picture", "upscale this image". Use for any request to create or modify a still visual asset.
---

# fal-image

Image generation, editing, upscaling, and batch variations via fal.ai. Constructs disciplined prompts using a 5-component formula and per-domain styling, calls the fal MCP, saves outputs project-locally with a JSON sidecar.

Two-layer architecture: this orchestrator handles intent detection, MCQs, fal calls, and file writes. A skill-local Sonnet subagent at `agents/brief-constructor.md` owns prompt construction. References under `references/` are loaded on demand by the subagent.

---

## Pre-flight (every invocation)

1. **CWD safety check.** If `pwd` is `$HOME`, `/`, `/etc`, `/usr`, `/var`, or any other system path: warn the user and ask whether to (a) write to fallback `~/Documents/vizkit-outputs/<date>/...` or (b) continue in the current directory. Do not silently pollute system folders.

2. **fal MCP discovery.** `ToolSearch` for `fal-ai` to confirm the 9 `mcp__fal-ai__*` tools are loaded (`recommend_model`, `get_pricing`, `get_model_schema`, `run_model`, `submit_job`, `check_job`, `upload_file`, `search_models`, `search_docs`). If absent, register via `claude mcp add --transport http --scope user fal-ai https://mcp.fal.ai/mcp --header "Authorization: Bearer <FAL_KEY>"` and restart the session. Tool flow + auth gotchas live in `references/fal-mcp-flow.md`.

3. **Allowlist (optional but recommended for repeated work).** Add `mcp__fal-ai` to `permissions.allow` in `.claude/settings.local.json` to skip per-call permission prompts.

4. **Mode detection.** Parse the user's message to determine mode:
   - **generate** — text-to-image (default)
   - **edit** — user provided source image + modification verb
   - **upscale** — user provided source image + "upscale" / "make bigger" / "enhance"
   - **batch** — user asked for "N variations", "options", "variants"

---

## Model roster

| Model | Endpoint | When it fits | Prompt opening |
|---|---|---|---|
| **Nano Banana Pro** *(primary)* | `fal-ai/nano-banana-pro` | Most image work — photoreal hero, complex composition, character/style consistency, multi-image fusion (up to 14 references), conversational iterative edits | Subject + scene context, conversational, world-aware |
| **Recraft V4 Pro** | `recraft/v4/pro/text-to-image` | When the output needs to be SVG / vector — logos, brand marks, scalable artwork | Describe the artifact ("flat geometric two-color mark") |
| **Ideogram V3** | `fal-ai/ideogram/v3` | Dense, decorative, multi-line typography — magazine covers, posters with paragraph text, headline-driven layouts | One-line scene summary, then literal text in quotes early, then style |
| **Flux 2 [pro]** | `fal-ai/flux-2-pro` | Cheaper alternative for photoreal hero work when iterating, when budget matters, or when Nano Banana over-stylizes | Subject-first, front-loaded; HEX colors directly in prompt |
| **Flux Kontext [pro]** | `fal-ai/flux-pro/kontext` | Single-reference conversational edit — the workhorse edit model at $0.04 | Imperative ("change the jacket to red"); name subjects, no pronouns |

These are the primary candidates. Pick the one whose strengths match the request. Fall back to `recommend_model` from fal MCP if the named model is unavailable or the user asks for something outside this list.

---

## Pipeline

### 1. Detect domain

Read `references/domains.md`. Match the user's request against detection cues. Pick the domain with highest confidence. If two+ tie above 60%, ask the disambiguation MCQ first (per `references/clarification-mcq.md`). If none match above 60%, ask the disambiguation MCQ with top-3 candidates.

### 2. Resolve preset

This skill is **project-scoped** (lives at `<project-root>/.claude/skills/fal-image/`). At runtime, compute the skill root by resolving `$PWD` (or equivalent absolute CWD) at session start. The skill root is `$PWD/.claude/skills/fal-image/`.

Default preset: `$PWD/.claude/skills/fal-image/presets/<domain>.preset.md` — pass the absolute expanded path (no `~`, no shell variables) to the Read tool.

Custom: if the user wrote `using @./brand.preset.md` or `using ./path/to/preset.md`, resolve the absolute path and use that instead.

### 3. Evaluate formula gaps

Read `references/clarification-mcq.md` for the gap-counting heuristic. For each of the 5 formula slots, decide if it's filled (by message + preset) or a gap. Count gaps.

### 4. Render content MCQs (if any)

If gaps exist, render up to 2 content MCQs in plain markdown chat (NOT via the AskUserQuestion tool). Use the patterns from `references/clarification-mcq.md`. Skip if user said "just generate" / fully-specified brief.

### 5. Pick the model

Choose from the roster based on the request:
- SVG / vector / brand mark → Recraft V4 Pro
- Dense headline / paragraph typography → Ideogram V3
- Edit with a single reference image → Flux Kontext [pro]
- Iteration, draft, "rough version", explicit budget concern → Flux 2 [pro]
- Multi-reference fusion, character consistency, premium hero → Nano Banana Pro
- Anything else → Nano Banana Pro

If the user named a model, honor it. Pass `target_model: "<short-name>"` to the brief-constructor so it can adapt the prompt opening.

### 6. Spawn brief-constructor subagent

Use the `Task` tool with `subagent_type: "general-purpose"`. Wrapper prompt (substitute the actual absolute path computed from `$PWD`):

> "Read `<absolute-skill-root>/agents/brief-constructor.md` and follow its instructions exactly. Then construct a prompt with these inputs: skill-root=`<absolute-skill-root>`, user request, domain, preset path (absolute), mode, target_model, reference images (path/URL + role per image, if any), MCQ answers, custom override notes, batch info if applicable. Your entire reply must be only the prompt string — nothing before, nothing after, no markdown fence, no explanation."

Where `<absolute-skill-root>` is `$PWD/.claude/skills/fal-image/` resolved to an absolute path.

Capture the reply. Pipe through `scripts/orchestrator.py: strip_preamble()` — defensively removes any leading meta-narration the brief-constructor leaks past its contract. If reply starts with `BRIEF_FAILED:`, surface the reason and stop.

### 7. Pre-flight summary

Before calling fal, print a four-line summary in chat:

- **Domain** — detected domain
- **Model** — chosen endpoint + one-line reason ("Nano Banana Pro for premium photoreal with multi-reference fusion")
- **Prompt** — the brief-constructor's output, in a code block
- **Cost** — `get_pricing(endpoint_id)` estimate

Wait for user response. Proceed on confirmation ("looks good", "go", "yes"). Adjust on redirect ("use Flux 2 instead", "drop the cinematic register", "smaller scale").

### 8. Call fal MCP

Image generation is fast (~150ms) — use the synchronous `run_model` flow. Canonical sequence (full reference: `references/fal-mcp-flow.md`):

1. `get_model_schema(endpoint_id)` → verify endpoint exists + read input params (halt if schema errors)
2. `run_model(endpoint_id, input)` → returns the image URL + seed

Pass the constructed prompt with: aspect ratio from preset (override if user specified), resolution from preset or sensible default, reference image URLs in the schema's reference-input field if applicable, other params per model schema.

On transient failure (timeout, 5xx): one silent retry after 2 seconds. On second failure: report error, do not retry.

### 9. Post-call file writes

Use `scripts/orchestrator.py` helpers — `slug_from_request()`, `next_version()`, `download_to_local()`, `write_sidecar()`, `strip_preamble()`. Full schema in `references/outputs.md`. TL;DR:

1. **Compute slug + version** by scanning `<cwd>/generated/images/<date>/`.
2. **mkdir -p** the date folder.
3. **Download image** to `<slug>-vNN.<ext>` from the fal CDN URL.
4. **Write JSON sidecar** at `<slug>-vNN.json` — include `params.request_id`, `params.model`, `params.model_choice_reason`, `params.reference_images` (if any), `params.preflight_confirmed`.
5. **Verify** both files exist with non-zero size. On any partial-write failure: echo the full sidecar JSON to chat as fallback log; never delete an image that was saved successfully — the user paid for it.

### 10. Report to user

In chat, output:

- **Path** (relative): `generated/images/<date>/<slug>-vNN.<ext>`
- **Cost incurred** in USD
- **1–2 refinement suggestions** ("want a moodier version?", "want a different angle?")

---

## Mode-specific notes

### Edit mode

Routes here when the user provides a source image + modification verb. The reference image's role — style match, character preserve, composition lock, or direct edit target — is inferred from the user's phrasing (e.g., "change the jacket to red" = direct edit target on Flux Kontext; "in the style of this poster" = style reference; "use this person across these four scenes" = character reference suiting Nano Banana Pro's multi-image fusion). Pass the role to the brief-constructor so it can phrase the reference into the prompt correctly. Upload local sources via the direct fal REST pattern in `references/editing.md`.

### Upscale mode

Routes here when the user provides source + "upscale" intent. Bypass the brief-constructor (no prompt needed). Show scale-factor options (2x default, 4x available with cost note). Save output with `<source-slug>-upscaled-vNN` if source has a known slug, else `upscale-<6char-hash>-vNN`.

### Batch mode

Routes here when the user asks for N variations. Ask the rotation MCQ if not specified. Lock 4 of 5 formula slots, rotate the 5th. Call brief-constructor N times with each variation's value. Save N outputs as `<slug>-v01` through `<slug>-vNN`. Report total cost = N × per-image.

Cap N at 6 by default; confirm with user before exceeding.

---

No emojis. No meta-commentary. The prompt sent to fal is exactly what brief-constructor returned, post `strip_preamble()` — nothing added.
