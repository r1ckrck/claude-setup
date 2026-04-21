# Claude Code — Custom Statusline

A native two-line statusline for Claude Code, with no plugins or runtime dependencies beyond what you already have. Replaces plugin-based options like `claude-hud`.

## What it looks like

```
 󰚩 Opus 4.7  high    ~/project   main ↑1 · 3h ago 

 cache 96% │ 󰚋 ctx ███░░░░░░░ 32% │  5h █████░░░░░ 55% ↻ 2h 30m │  7d 28% ↻ 5d 0h │  api 8m 12s │ $ 0.45
```

- **Line 1 — identity**: model pill + effort pill (chained) · folder → git (chained arrows in the blue family — same hue, different shades, so folder + its repo state read as one unit)
- **Line 2 — metrics**: cache hit · context · 5h usage · 7d usage · API wait · session cost
- Nerd-font icons, ANSI colors pulled from your terminal palette
- Progress bars that shift green → yellow → red as usage climbs
- Model pill color changes by family (Opus violet, Sonnet blue, Haiku green)
- Effort pill color ramps cool grey → warm amber as effort climbs; absent when unset
- Git segment turns solid red when the working tree is dirty

> **Note on colors**: When Sonnet is selected, the model pill and the CWD arrow are both in the blue family. The *shapes* still distinguish them (rounded pill vs. arrow chain). This is an intentional trade-off — keeping folder + git as a chromatically unified pair was judged more valuable than avoiding the occasional blue-on-blue pairing.

## Requirements

1. **Claude Code** (any recent version)
2. **`jq`** (`brew install jq` — likely already present at `/usr/bin/jq`)
3. **`git`** (already on macOS)
4. **A Nerd Font** installed and set as your terminal font. Recommended:
   ```
   brew install --cask font-jetbrains-mono-nerd-font
   ```
   Then set your terminal font to **JetBrainsMono Nerd Font Mono**.

   Without a nerd font, every icon will render as a `□` placeholder.

## Install

1. **Copy the script to `~/.claude/statusline.sh`**:
   ```bash
   cp statusline.sh ~/.claude/statusline.sh
   chmod +x ~/.claude/statusline.sh
   ```

2. **Add the `statusLine` block to `~/.claude/settings.json`**. Open `settings.json` and add the top-level key shown in `settings.snippet.json` (replace `YOUR_USER` with your macOS username, or use `$HOME`):
   ```json
   "statusLine": {
     "type": "command",
     "command": "bash /Users/YOUR_USER/.claude/statusline.sh"
   }
   ```

3. **Set your terminal font to a nerd font** (see Requirements).

4. **Restart Claude Code** (or start a new session). The statusline appears automatically.

## Configure the terminal font (VS Code)

Add to VS Code `settings.json`:
```json
"terminal.integrated.fontFamily": "JetBrainsMono Nerd Font Mono"
```

For iTerm2 / Terminal.app / other terminals, set the profile font to the same nerd font.

## What each element means

### Line 1 — identity

| Element | Meaning |
|---------|---------|
| 󰚩 Model name | Which Claude model is active. Pill color = model family (Opus violet, Sonnet blue, Haiku green). |
| Effort | Current `/effort` tier (Opus thinking level). Chained into the model pill. Absent when unset. |
|  Folder | Current working directory, `~` replaces `$HOME`. |
|  Branch | Git branch name + ahead/behind vs upstream + last commit age. |

**Dirty state**: if the working tree has uncommitted changes, the entire git segment's background turns **red**.

**Effort tiers** (values from `/effort` or `/model`; resolved from transcript → settings.json):

| Tier | Look | Meaning |
|------|------|---------|
| *(unset)* | pill omitted | Effort not configured — no segment drawn |
| `low` | grey bg · dim white fg | Minimal thinking — quiet, stays out of the way |
| `medium` | cyan bg · bright white fg | Cool, engaged |
| `high` | yellow bg · **bold** black fg | Warm — the everyday high-effort default |
| `xhigh` | bright yellow bg · **bold** black fg | Hot — Opus 4.7 only |
| `max` | red bg · **bold** white fg · ✦ prefix | Full tilt — signature state |

Each tier uses a **distinct hue** so the effort level is recognizable at a glance without reading the label. The ramp walks cool → warm → hot: grey → cyan → yellow → amber → red.

> **Note on red**: Red also appears on a dirty git tree. The two don't conflict — git red sits in the arrow chain after the folder, effort red sits chained into the model pill at the very left. The `✦` marker on `max` further separates it from an accidental "red = warning" read. If you'd rather not share the hue at all, swap `effort_bg=41` to `effort_bg=105` (magenta) or `106` (bright cyan) in `statusline.sh`.

**Model-specific tiers**:
- **Opus 4.7** supports all five: `low`, `medium`, `high`, `xhigh`, `max`
- **Opus 4.6 / Sonnet 4.6** cap at `max` — there is no `xhigh` tier

### Line 2 — metrics

| Element | Meaning |
|---------|---------|
|  cache % | % of input tokens served from Anthropic's prompt cache on the last turn. Higher = cheaper / faster. |
| 󰚋 ctx bar % | % of the context window filled. 200k or 1M window, detected from the model ID. |
|  5h bar % ↻ | Usage against Anthropic's 5-hour rolling quota + time until it resets. |
|  7d bar % ↻ | Usage against Anthropic's 7-day quota + time until it resets. |
|  api | Total time Claude Code spent waiting on API responses this session. |
| $ | This session's cumulative spend (USD). |

### Color scale

| Usage-like metrics (ctx, 5h, 7d) | Color |
|----------------------------------|-------|
| 0–49% | 🟢 green — safe |
| 50–74% | 🟡 yellow — watch |
| 75–89% | 🟠 bright red — warning |
| ≥ 90% | 🔴 red bold — critical |

| Cache hit % (reversed — higher is better) | Color |
|-------------------------------------------|-------|
| ≥ 70% | 🟢 green — good caching |
| 40–69% | 🟡 yellow — mediocre |
| < 40% | 🔴 bright red — almost nothing cached |

## Where the data comes from

Claude Code pipes a JSON payload to the script's `stdin` on every refresh. Key fields used:

- `model.display_name`, `model.id` — model pill
- `workspace.current_dir` — folder segment
- `transcript_path` — parsed for last-turn usage (ctx %, cache hit %)
- `cost.total_cost_usd`, `cost.total_api_duration_ms` — cost + API wait
- `rate_limits.five_hour.{used_percentage, resets_at}` — 5h quota
- `rate_limits.seven_day.{used_percentage, resets_at}` — 7d quota

`rate_limits` are populated by Claude Code itself (server-authoritative) — no third-party usage tool needed.

**Effort level** isn't in the stdin payload. The script resolves it from two sources:

1. **Session transcript** (`transcript_path`) — the most recent `Set model to … with <level> effort` line.
2. **`~/.claude/settings.json`** (`effortLevel`) — used when the transcript has no in-session change. Respects `$CLAUDE_CONFIG_DIR`.

## Performance

One `jq` call + a handful of `git` commands. Measured at 10–30 ms per refresh. Well under the ~300 ms threshold where statuslines feel sluggish.

## Customizing

All colors are ANSI 16 codes (e.g. `31` = red, `44` = blue bg, `95` = bright magenta), so the palette automatically follows your terminal's theme — **don't hardcode hex values**.

Common tweaks in `statusline.sh`:

- **Model pill hues** — search for `case "$model_lc"` and change the `model_bg` value (40–47 or 100–107 range).
- **Effort ramp** — search for `case "$effort"` and adjust `effort_bg` / `effort_fg` per tier.
- **Threshold colors** — see `pct_fg()` and `cache_fg()` functions.
- **Icons** — search for `ICO_*` variables. Each is a raw UTF-8 sequence for a nerd-font private-use-area codepoint; replace with the UTF-8 for a different nerd-font glyph.
- **Remove a segment** — delete the corresponding `add ...` block in the Line 2 section.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Icons show as `□` | Terminal font isn't a nerd font. Install and configure one (see Requirements). |
| No 5h / 7d segments | Usage data isn't populated until the first assistant response in the session. Send a message, it'll appear. Also won't appear for API-key-only or Bedrock/Vertex setups. |
| No context %, no cache % | Requires at least one assistant turn in the session so the transcript has a `usage` entry. |
| Statusline doesn't show at all | Confirm the `statusLine` block is in `~/.claude/settings.json` and the script path is correct. Try running the script manually with a dummy JSON: `echo '{}' \| bash ~/.claude/statusline.sh`. |
| Colors are wrong / gray | Terminal might not support 16-color ANSI. Nearly all modern terminals do — check terminal settings. |

## Files in this folder

- `statusline.sh` — the script
- `settings.snippet.json` — the `statusLine` block to add to `~/.claude/settings.json`
- `README.md` — this file
