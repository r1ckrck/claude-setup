# Image Generation Setup Plan
## Stack: Claude Code + fal.ai + banana-claude skill

---

## Overview

The goal is a clean image generation setup inside Claude Code with three components working together:

- **Claude Code** — the backbone and interface. You talk to it, it runs everything.
- **fal.ai** — the generation engine. Provides access to 1,000+ models (Flux, SDXL, Recraft, video, audio) via a single API key.
- **Skill** — a markdown file that gives Claude instructions on how to behave when you invoke it. Adapted from banana-claude's prompt engineering methodology, domain categories, and workflow — but wired to fal.ai instead of Gemini.

---

## Part 1 — fal.ai Setup

### 1.1 Get a FAL_KEY

1. Go to [fal.ai](https://fal.ai) and create an account
2. Navigate to the dashboard → API Keys
3. Click **Create Key** — scope: `API`
4. Copy it immediately (only shown once)

### 1.2 Add the Official fal MCP to Claude Code

fal runs their own hosted MCP server at `https://mcp.fal.ai/mcp`. Nothing to install locally — just add one entry to `~/.claude/settings.json`.

In your `~/.claude/settings.json`, add to the `mcpServers` block:

```json
"mcpServers": {
  "fal": {
    "url": "https://mcp.fal.ai/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_FAL_KEY"
    }
  }
}
```

Also add the MCP tool permissions to your `permissions.allow` array:

```json
"mcp__fal__run_model",
"mcp__fal__submit_job",
"mcp__fal__check_job",
"mcp__fal__upload_file",
"mcp__fal__search_models",
"mcp__fal__get_model_schema",
"mcp__fal__get_pricing",
"mcp__fal__recommend_model"
```

### 1.3 What the fal MCP Gives You

| Tool | What Claude can do with it |
|---|---|
| `run_model` | Generate an image immediately with any model |
| `submit_job` | Queue a longer job (video, high-res) |
| `check_job` | Poll a queued job for its result |
| `upload_file` | Upload a local image to fal CDN before editing |
| `search_models` | Find models by keyword ("flux", "portrait", "upscale") |
| `get_model_schema` | Get exact parameters a model accepts |
| `get_pricing` | Check cost before running |
| `recommend_model` | Ask fal AI to suggest the right model for a task |

### 1.4 Models to Know (Starting Points)

| Model ID | Use |
|---|---|
| `fal-ai/flux/schnell` | Fast drafts, prototyping |
| `fal-ai/flux-pro/v1.1` | Production quality images |
| `fal-ai/flux-pro/kontext` | Edit an existing image with a prompt |
| `fal-ai/recraft-v3` | Professional product/editorial work |
| `fal-ai/clarity-upscaler` | Upscale generated images |
| `fal-ai/kling-video/v3/pro/text-to-video` | Text to video |

These are starting defaults. The `search_models` tool surfaces others on demand.

---

## Part 2 — Skill Setup

The skill is a folder of markdown files that Claude reads when you invoke it. No code, no runtime — just instructions Claude follows.

### 2.1 Directory Structure

```
~/.claude/
└── skills/
    └── image/
        ├── SKILL.md                    ← Main skill file (Claude reads this on /image)
        └── references/
            ├── prompt-engineering.md   ← 5-component formula, templates, banned keywords
            └── domains.md              ← Domain categories and their style vocabularies
```

Create the directories:

```bash
mkdir -p ~/.claude/skills/image/references
```

### 2.2 The Three Files to Create

#### `~/.claude/skills/image/SKILL.md`

This is the main behavior file. When you type `/image`, Claude reads this and follows it.

Contents:

```markdown
# Image Generation Skill

## Trigger
Activate on `/image` commands or any request to generate, create, or edit an image.

## Available Commands
| Command | Purpose |
|---------|---------|
| `/image generate <idea>` | Generate an image with full prompt engineering |
| `/image edit <path> <instructions>` | Edit an existing image |
| `/image batch <idea> [N]` | Generate N variations |
| `/image find <keyword>` | Search for the right model |

## Workflow — Every generation must follow these steps

### Step 1 — Identify the Domain
Determine which domain category fits the request:
- **Cinema** — narrative scenes, film stills, dramatic lighting
- **Product** — commercial photography, packshots, advertising
- **Portrait** — people, editorial portraits, lifestyle
- **Editorial** — fashion, magazine spreads, styled shoots
- **UI** — interface mockups, dashboards, app screens
- **Logo** — wordmarks, icons, brand marks
- **Landscape** — environments, architecture, nature
- **Abstract** — generative, geometric, texture, art
- **Infographic** — data visualization, diagrams, charts

If unclear, ask the user: "Is this closer to [A] or [B]?"

### Step 2 — Construct the Prompt
Load `references/prompt-engineering.md` and apply the 5-Component Formula.
NEVER pass the user's raw words directly to the model.
Build a full narrative prompt of 100–200 words.

### Step 3 — Select Model and Aspect Ratio
Default model: `fal-ai/flux-pro/v1.1`
Default aspect ratio: `landscape_4_3`

Adjust based on domain:
- Portrait/stories: `portrait_16_9`
- Square/social: `square_hd`
- Cinematic: `landscape_16_9`
- Infographic/UI: `square_hd` or `portrait_4_3`

For model selection, use `recommend_model` or `search_models` if needed.

### Step 4 — Execute
Call `run_model` with the constructed prompt and parameters.
If the request is video or a long high-res job, use `submit_job` + `check_job`.

### Step 5 — Report Back
Return the image URL and the exact prompt used so the user can refine it.

## Key Rules
- Never use banned keywords: "8K", "masterpiece", "ultra-detailed", "photorealistic", "best quality"
- Always write prompts as narrative prose — never comma-separated keywords
- Use prestigious context anchors instead: "Vanity Fair editorial", "National Geographic cover", "Architectural Digest"
- For editing, always `upload_file` first to get a CDN URL, then use `fal-ai/flux-pro/kontext`
```

#### `~/.claude/skills/image/references/prompt-engineering.md`

Copy directly from banana-claude — this file is model-agnostic (pure prompt methodology).

```bash
curl -s https://raw.githubusercontent.com/AgriciDaniel/banana-claude/main/skills/banana/references/prompt-engineering.md \
  -o ~/.claude/skills/image/references/prompt-engineering.md
```

The relevant parts (model-agnostic):
- The 5-Component Formula (Subject → Action → Location → Composition → Style)
- Banned keywords list
- Proven prompt templates per domain
- Text rendering rules
- Safety filter rephrase strategies

Remove or ignore any Gemini-specific sections (`set_aspect_ratio` MCP tool calls, `gemini_chat`, search grounding).

#### `~/.claude/skills/image/references/domains.md`

Copy the Domain Mode Modifier Libraries section from banana-claude's prompt-engineering.md. This is also model-agnostic — it's just style vocabulary per domain. Keep everything:

- Cinema: camera specs, film stocks, lighting setups, shot types
- Product: surfaces, lighting, angles, style refs
- Portrait: focal lengths, apertures, pose language
- Editorial: publication refs, styling, locations, poses
- UI: styles, colors, sizing, backgrounds
- Logo: construction, typography, colors
- Landscape: depth layers, atmospherics, time of day
- Infographic: layout, text hierarchy, data viz
- Abstract: geometry, textures, color palettes

---

## Part 3 — How It All Connects

```
You type:  /image generate "product shot of a coffee cup, dark moody"
               ↓
Claude reads SKILL.md
               ↓
Identifies domain: Product
               ↓
Loads references/prompt-engineering.md + references/domains.md
               ↓
Constructs 150-word narrative prompt using Product style vocabulary:
"A matte black ceramic coffee cup placed on a slate grey textured surface,
steam rising in a gentle curl, shot from a 45-degree hero angle.
Studio tent lighting with a single hard key from camera right,
deep shadow on the left creating dramatic contrast.
Condensation rings visible on the surface from a previous cup.
Shot on Sony A7R IV, 85mm macro lens, f/2.8.
Apple product photography aesthetic, Wallpaper* magazine editorial feel."
               ↓
Calls fal MCP:  run_model("fal-ai/flux-pro/v1.1", {prompt: "...", image_size: "landscape_4_3"})
               ↓
Returns URL + prompt used
```

---

## Part 4 — What to Do Later (Not Required Now)

These are optional expansions once the core is working:

- **Add video support** — `/image video` that routes to `fal-ai/kling-video/v3/pro/text-to-video` or `fal-ai/veo3.1`
- **Add upscaling** — `/image upscale <path>` using `fal-ai/clarity-upscaler`
- **Add presets** — Brand style presets stored as JSON in `~/.claude/skills/image/presets/`
- **Add a subagent** — A `brief-constructor` agent (adapted from banana-claude) that Claude delegates prompt construction to, keeping SKILL.md lean
- **Cost tracking** — A simple Python script that logs each run_model call with model + timestamp

---

## Summary Checklist

- [ ] Create account on fal.ai and get `FAL_KEY`
- [ ] Add fal MCP entry to `~/.claude/settings.json` with the key
- [ ] Add fal MCP tool permissions to `permissions.allow` in settings
- [ ] Create `~/.claude/skills/image/` directory structure
- [ ] Write `SKILL.md` (domain detection → prompt construction → fal execution)
- [ ] Fetch `prompt-engineering.md` from banana-claude repo
- [ ] Extract domain vocabulary into `domains.md`
- [ ] Test with `/image generate` on a simple prompt
