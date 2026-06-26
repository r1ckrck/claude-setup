---
name: gif-maker
description: Create animated GIFs from scratch by orchestrating fal-video (source clip) + media-processing (GIF conversion). Triggers on requests like "make a gif of X", "create an animated gif of X", "generate a gif of X" — when no existing video file is provided. If the user has an existing video file to convert, use media-processing instead.
---

# gif-maker

Animated GIF generation by orchestrating fal-video (source clip) + ffmpeg (palette + paletteuse). Pure orchestrator: no own brief-constructor (spawns fal-video's), defaults to Kling 2.5 Turbo Pro for source-clip generation. Has a single `default.preset.md` for GIF output defaults.

**Sibling-skill dependency:** gif-maker requires the `fal-video` skill installed at `$PWD/.claude/skills/fal-video/` and ffmpeg present locally. Both are checked in pre-flight.

---

## Pre-flight (every invocation)

1. **CWD safety check.** If `pwd` is `$HOME`, `/`, `/etc`, `/usr`, `/var`, or any other system path: warn the user and ask whether to (a) write to fallback `~/Documents/vizkit-outputs/<date>/...` or (b) continue. Do not silently pollute system folders.

2. **Sibling-skill check.** Verify `$PWD/.claude/skills/fal-video/agents/brief-constructor.md` exists. If absent: "gif-maker depends on the fal-video skill being installed at `<project>/.claude/skills/fal-video/`. Install it (or copy from a project that has it) before continuing."

3. **fal MCP discovery.** `ToolSearch` for `fal-ai` to confirm the 9 `mcp__fal-ai__*` tools are loaded (`recommend_model`, `get_pricing`, `get_model_schema`, `submit_job`, `check_job`, plus the rest). If absent, register via `claude mcp add --transport http --scope user fal-ai https://mcp.fal.ai/mcp --header "Authorization: Bearer <FAL_KEY>"` and restart. Tool flow + auth gotchas live in `references/fal-mcp-flow.md`.

4. **Allowlist (recommended).** Add `mcp__fal-ai` to `permissions.allow` in `.claude/settings.local.json` to skip per-call permission prompts — critical here, where the source-clip pipeline does one `submit_job` plus multiple `check_job` polls per GIF.

5. **ffmpeg presence check.** Run `ffmpeg -version`. If missing: install via `brew install ffmpeg` (macOS) / `apt install ffmpeg` (Debian) / `choco install ffmpeg` (Windows), then retry.

---

## Source-clip model

Default endpoint: **`fal-ai/kling-video/v2.5-turbo/pro/text-to-video`** (or `.../image-to-video` when the user provides a source still). Cheap workhorse at ~$0.07/s — well-suited to GIFs since they discard audio anyway and rarely need premium fidelity. The user can override to Veo 3.1 (`fal-ai/veo3.1`) for hero or photographic intents that warrant the quality jump; the orchestrator surfaces the choice and cost in the pre-flight summary.

---

## Pipeline

### 1. Detect intent

Read `references/strategy.md`. Classify the request into one of 5 intents: `loader`, `micro-animation`, `hero`, `decorative`, `photographic`. If the cues don't match any single intent cleanly, ask one disambiguation MCQ (per `references/strategy.md` "When intent is unclear" section). If user provides a video file path, suggest routing to `media-processing` instead.

### 2. Resolve preset

Default: `$PWD/.claude/skills/gif-maker/default.preset.md` — pass the absolute expanded path to the Read tool. If user wrote `using @./brand-gif.preset.md`, resolve and use that instead.

### 3. Determine GIF parameters

From intent + preset + user overrides:
- **fps** — default 10, override range 8–15
- **width** — default 480px, override allowed (320 / 640 / 720 typical alternatives)
- **max_colors** — 16–32 for loader/micro-animation, 64 for hero, 32–64 for decorative, 128 for photographic
- **dither** — `bayer` for flat content, `floyd_steinberg` for photographic
- **duration** — default model minimum (Kling supports 5s); trim with ffmpeg `-t` if user wants shorter
- **aspect ratio** — per user intent (square for buttons / 16:9 for hero / vertical for stories)

### 4. Read source-clip-spec

Read `references/source-clip-spec.md`. Build the override-notes block from the template, substituting per-intent values (color budget phrasing, loop phrasing, duration, aspect ratio).

### 5. Spawn fal-video's brief-constructor as subagent

Use the `Task` tool with `subagent_type: "general-purpose"`. Wrapper prompt (substitute the actual absolute path computed from `$PWD`):

> "Read `$PWD/.claude/skills/fal-video/agents/brief-constructor.md` and follow its instructions exactly. Then construct a prompt with these inputs: skill-root=`$PWD/.claude/skills/fal-video`, user request=<verbatim>, detected domain=<per intent mapping in strategy.md>, preset path=`$PWD/.claude/skills/fal-video/presets/<domain>.preset.md`, mode=generate, target_model=`kling-2.5-turbo-pro`, audio_enabled=false, MCQ answers=none, custom override notes=<the GIF-aware block built in step 4>, target duration=<chosen source duration>, target fps=accept native — fps not controllable on most fal models. Your entire reply must be only the prompt string — nothing before, nothing after, no markdown fence, no explanation."

Capture the reply. Pipe through `scripts/orchestrator.py: strip_preamble()` — defensively removes leading meta-narration the brief-constructor leaks past its contract. If reply starts with `BRIEF_FAILED:`, surface the reason and stop.

### 6. Pre-flight summary

Before submitting to fal, print a summary in chat:

- **Intent** — detected intent (loader / micro-animation / hero / decorative / photographic)
- **Source model** — chosen endpoint + one-line reason ("Kling 2.5 Turbo Pro for cheap workhorse iteration")
- **Source prompt** — the brief-constructor's output, in a code block
- **GIF params** — fps, width, max colors, dither, duration
- **Cost** — `get_pricing(endpoint_id)` estimate at the chosen duration

Wait for user response. Proceed on confirmation. Adjust on redirect ("use Veo for premium", "shorter clip", "fewer colors").

### 7. Call fal MCP for source-clip generation

Source clips run 30–90s — **always use `submit_job` + `check_job` polling, never `run_model`**. Sync-poll times out unreliably while fal still queues the job, leaving an orphan you can't recover. Canonical sequence (full reference: `references/fal-mcp-flow.md`):

1. `get_model_schema(endpoint_id)` → verify endpoint exists + read input params (halt if schema errors)
2. `submit_job(endpoint_id, input)` → returns `{request_id}` IMMEDIATELY — capture and persist before anything else
3. Poll `check_job(endpoint_id, request_id, action="status")` every 10–15s; when `status="completed"`, fetch `action="result"`

Default request: smallest resolution tier, audio off, model-minimum duration, aspect ratio per intent. User override allowed for model + duration only — other params locked. Capture `request_id` from the submit response into `params.request_id` immediately so the job is recoverable if the poll loop fails.

### 8. Save source MP4

Use `scripts/orchestrator.py: slug_from_request()` and `next_version()` to compute slug + version. Save the MP4 to `<cwd>/generated/gifs/<date>/_source/<slug>-vNN-source.mp4` via `download_to_local()`. The underscore prefix sorts the source folder to bottom; the MP4 is kept so the user can re-encode without re-paying fal.

### 9. Run ffmpeg two-pass palette pipeline

Run the two-pass pipeline per `references/ffmpeg-commands.md`: `palettegen` → palette PNG, then `paletteuse` → final GIF. Capture both literal command strings into `params.ffmpeg_pass1` / `params.ffmpeg_pass2` so future re-encoding doesn't require re-running gif-maker. Discard the intermediate palette PNG after pass 2.

### 10. Save GIF

Final GIF lands at `<cwd>/generated/gifs/<date>/<slug>-vNN.gif`.

### 11. Write JSON sidecar

At `<slug>-vNN.json` via `scripts/orchestrator.py: write_sidecar()` with these fields:
- `request`, `slug`, `version`, `type: "gif"`, `skill: "gif-maker"`, `prompt` (brief-constructor output, post-strip)
- `params.fal_model`, `params.model_choice_reason`, `params.preflight_confirmed`, `params.source_duration_seconds`, `params.gif_fps`, `params.gif_width`, `params.gif_max_colors`, `params.gif_dither`, `params.intent`, `params.source_path`, `params.request_id`, `params.ffmpeg_pass1`, `params.ffmpeg_pass2`
- `cost_usd`, `timestamp` (ISO 8601 with offset), `duration_ms`, `output_path` (relative)

### 12. Verify and report

Verify all three files exist with non-zero size: GIF + sidecar + source MP4. On any partial-write failure: echo full sidecar JSON to chat as fallback log; never delete the source MP4 (user paid for it).

In chat, output:
- **Path** (relative): `generated/gifs/<date>/<slug>-vNN.gif`
- **Source MP4 path** (kept): `generated/gifs/<date>/_source/<slug>-vNN-source.mp4`
- **Cost incurred** in USD
- **1–2 refinement suggestions** ("want it shorter / wider / fewer colors / different dither?") tuned to intent

---

No emojis. No meta-commentary. The prompt sent to fal-video's brief-constructor is exactly what's returned, post `strip_preamble()`. No motion-speed manipulation (no `setpts`, no playback-speed dialing). Color budget is intent-driven aesthetic guidance, never a literal "use N colors" prompt instruction.
