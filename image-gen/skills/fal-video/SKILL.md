---
name: fal-video
description: Generate text-to-video or image-to-video clips via fal.ai. Triggers on requests like "make a video", "generate a clip of X", "create a short video", "animate this image", "animate X", "bring X to life", "image-to-video". Use for video generation. Do NOT use for converting an existing video to a GIF (that's media-processing) or for creating a GIF from scratch (that's gif-maker).
---

# fal-video

Video generation via fal.ai. Constructs disciplined prompts using a 6-component formula (Subject → Action → Location/Context → Composition → Motion → Style+Lighting) and per-domain styling, calls the fal MCP, saves outputs project-locally with a JSON sidecar.

Two-layer architecture: this orchestrator handles intent detection, MCQs, fal calls, and file writes. A skill-local Sonnet subagent at `agents/brief-constructor.md` owns prompt construction. References under `references/` are loaded on demand by the subagent.

---

## Pre-flight (every invocation)

1. **CWD safety check.** If `pwd` is `$HOME`, `/`, `/etc`, `/usr`, `/var`, or any other system path: warn the user and ask whether to (a) write to fallback `~/Documents/vizkit-outputs/<date>/...` or (b) continue in the current directory. Do not silently pollute system folders.

2. **fal MCP discovery.** `ToolSearch` for `fal-ai` to confirm the 9 `mcp__fal-ai__*` tools are loaded (`recommend_model`, `get_pricing`, `get_model_schema`, `run_model`, `submit_job`, `check_job`, `upload_file`, `search_models`, `search_docs`). If absent, register via `claude mcp add --transport http --scope user fal-ai https://mcp.fal.ai/mcp --header "Authorization: Bearer <FAL_KEY>"` and restart the session. Tool flow + auth gotchas live in `references/fal-mcp-flow.md`.

3. **Allowlist (recommended for video work).** Add `mcp__fal-ai` to `permissions.allow` in `.claude/settings.local.json` to skip per-call permission prompts — critical for video, where a rejected `submit_job` or `check_job` poll can orphan a running job.

4. **Mode detection.** Parse the user's message to determine mode:
   - **generate** — text-to-video (default)
   - **i2v** — user provided source image + motion verb ("animate this", "bring this to life", "make this move")
   - **batch** — user asked for "N variations", "options", "variants"

---

## Model roster

| Model | Endpoint | When it fits | Prompt opening |
|---|---|---|---|
| **Veo 3.1** *(primary)* | `fal-ai/veo3.1` (T2V) · `fal-ai/veo3.1/image-to-video` (I2V) | Most video work — cinematic register, realistic motion, native audio + lip-sync, strong fidelity-to-source on I2V | Cinematography-first (shot type, camera move, lens) |
| **Kling 2.5 Turbo Pro** | `fal-ai/kling-video/v2.5-turbo/pro/text-to-video` · `.../image-to-video` | Cheaper alternative for iteration, scratch work, draft passes — about an eighth the cost of Veo | Subject-first + explicit motion verb, director's voice |

These are the primary candidates. Pick by the request: cinematic / audio / hero work → Veo 3.1; iteration / draft / budget — Kling 2.5 Turbo Pro. Fall back to `recommend_model` from fal MCP for cases outside this list.

---

## Pipeline

### 1. Detect domain

Read `references/domains.md`. Match the user's request against detection cues. Pick the domain with highest confidence. If two+ tie above 60%, ask the disambiguation MCQ first (per `references/clarification-mcq.md`). If none match above 60%, ask the disambiguation MCQ with top-3 candidates.

### 2. Resolve preset

This skill is **project-scoped** (lives at `<project-root>/.claude/skills/fal-video/`). At runtime, compute the skill root by resolving `$PWD` (or equivalent absolute CWD) at session start. The skill root is `$PWD/.claude/skills/fal-video/`.

Default preset: `$PWD/.claude/skills/fal-video/presets/<domain>.preset.md` — pass the absolute expanded path (no `~`, no shell variables) to the Read tool.

Custom: if the user wrote `using @./brand.preset.md` or `using ./path/to/preset.md`, resolve the absolute path and use that instead.

### 3. Evaluate formula gaps

Read `references/clarification-mcq.md` for the gap-counting heuristic. For each of the 6 formula slots, decide if it's filled (by message + preset) or a gap. Count gaps.

### 4. Render content MCQs (if any)

If gaps exist, render up to 2 content MCQs in plain markdown chat (NOT via the AskUserQuestion tool). Use the patterns from `references/clarification-mcq.md`. **Motion is the top-priority MCQ for video** — ask it first if Motion is a gap. Skip if user said "just generate" / fully-specified brief.

### 5. Pick the model

Choose from the roster based on the request:
- Cinematic register, hero work, request mentions audio / sound / dialogue / music → Veo 3.1
- Draft, iteration, scratch, "rough version", explicit budget concern → Kling 2.5 Turbo Pro
- Anything else → Veo 3.1

If the user named a model, honor it. Pass `target_model: "<short-name>"` to the brief-constructor so it can adapt the prompt opening.

### 6. Spawn brief-constructor subagent

Use the `Task` tool with `subagent_type: "general-purpose"`. Wrapper prompt (substitute the actual absolute path computed from `$PWD`):

> "Read `<absolute-skill-root>/agents/brief-constructor.md` and follow its instructions exactly. Then construct a prompt with these inputs: skill-root=`<absolute-skill-root>`, user request, domain, preset path (absolute), mode, target_model, audio_enabled (boolean), reference images (path/URL + role per image, if any), MCQ answers, custom override notes, target duration if specified, target fps if specified, batch info if applicable. Your entire reply must be only the prompt string — nothing before, nothing after, no markdown fence, no explanation."

Where `<absolute-skill-root>` is `$PWD/.claude/skills/fal-video/` resolved to an absolute path.

Capture the reply. Pipe through `scripts/orchestrator.py: strip_preamble()` — defensively removes any leading meta-narration the brief-constructor leaks past its contract. If reply starts with `BRIEF_FAILED:`, surface the reason and stop.

### 7. Pre-flight summary

Before submitting to fal, print a summary in chat:

- **Domain** — detected domain
- **Model** — chosen endpoint + one-line reason ("Veo 3.1 for cinematic register with audio")
- **Audio** — on (with one-line description of the audio brief) or off
- **Prompt** — the brief-constructor's output, in a code block
- **Cost** — `get_pricing(endpoint_id)` estimate at the requested duration

Wait for user response. Proceed on confirmation. Adjust on redirect ("use Kling instead", "drop the dolly-in", "shorter clip").

### 8. Call fal MCP

Video generation runs 30–90 seconds — **always use `submit_job` + `check_job` polling, never `run_model`**. The sync-poll pattern times out unreliably while fal still queues the job, leaving an orphan you can't recover. Canonical sequence (full reference: `references/fal-mcp-flow.md`):

1. `get_model_schema(endpoint_id)` → verify endpoint exists + read input params (halt if schema errors)
2. `submit_job(endpoint_id, input)` → returns `{request_id}` IMMEDIATELY — capture and persist this before anything else
3. Poll `check_job(endpoint_id, request_id, action="status")` every 10–15s; when `status="completed"`, fetch `action="result"`

For i2v or any reference-image input: upload local sources via the direct fal REST API (2-step `POST storage/upload/initiate` → `PUT` bytes — full flow in `references/image-to-video.md`). Use the returned CDN URL as the model's reference input.

Pass: aspect ratio from preset (override if user specified), duration / fps from preset or user override, audio per the pre-flight decision, other params per model schema.

If a poll iteration rejects or the session disconnects, the `request_id` is the only recovery handle — `check_job(endpoint_id, request_id, action="result")` retrieves the completed video at any point within the CDN expiration window. Don't re-submit.

### 9. Post-call file writes

Use `scripts/orchestrator.py` helpers — `slug_from_request()`, `next_version()`, `download_to_local()`, `write_sidecar()`, `strip_preamble()`. Full schema in `references/outputs.md`. TL;DR:

1. **Compute slug + version** by scanning `<cwd>/generated/videos/<date>/`.
2. **mkdir -p** the date folder.
3. **Download video** to `<slug>-vNN.<ext>` from the fal CDN URL (default `.mp4`).
4. **Write JSON sidecar** at `<slug>-vNN.json` — include `params.request_id`, `params.model`, `params.model_choice_reason`, `params.audio_enabled`, `params.reference_images` (if any), `params.preflight_confirmed`.
5. **Verify** both files exist with non-zero size. On any partial-write failure: echo the full sidecar JSON to chat as fallback log; never delete a video that was saved successfully.

### 10. Report to user

In chat, output:

- **Path** (relative): `generated/videos/<date>/<slug>-vNN.<ext>`
- **Cost incurred** in USD
- **1–2 refinement suggestions** ("want a different camera move?", "want a longer/shorter duration?", "want it looping?")

---

## Mode-specific notes

### i2v / reference-image mode

Routes here when the user provides a source image. Read `references/image-to-video.md` for the upload mechanics and the role taxonomy — the source image's role (style match, character preserve, composition lock, animate-target) is inferred from the user's phrasing. Pass the resulting CDN URL plus the role to the brief-constructor so it can phrase the reference correctly. Source image already locks Subject/Location/Composition/Style — brief-constructor focuses on Motion + Action only. Prompt target length 50–120 words. Save output with slug `<source-slug>-animated-vNN.mp4` if source has known slug, else `animate-<verb>-vNN.mp4`.

### Batch mode

Routes here when user asks for N variations. Read `references/batch-variations.md`. Lock 5 of 6 formula slots, rotate the 1 chosen slot. **Default rotation: Motion** (most useful exploration axis for video). Ask the rotation MCQ if not specified. Call brief-constructor N times with each variation's value. Save N outputs as `<slug>-v01` through `<slug>-vNN`. Report total cost = N × per-clip.

**Cap N at 4 by default** — video runs more expensive than image generation, so a smaller batch keeps cost predictable. Confirm cost with user before exceeding.

---

## Audio default

Audio is **off** by default. Veo 3.1 doubles per-second cost when audio is enabled, and most short hero clips and downstream GIF conversion don't need audio. Audio turns on when the user explicitly mentions it ("with audio", "include sound", "add dialogue", "with music", "ambient sound") — at which point ask one short clarification about the audio register: ambient hum, specific sound effect, music cue, or spoken line. Pass `audio_enabled: true` and a one-line audio brief through to the brief-constructor; it weaves the audio language into the prompt (Veo 3.1 reads it from the prose).

---

No emojis. No meta-commentary. The prompt sent to fal is exactly what brief-constructor returned, post `strip_preamble()` — nothing added.
