# ffmpeg Commands — gif-maker

The exact two-pass ffmpeg pipeline gif-maker runs to convert a source MP4 into an optimized GIF. gif-maker runs these locally — no fal cost.

---

## Pre-conditions

Before running either pass:

1. `ffmpeg -version` returns successfully (verified in SKILL.md pre-flight)
2. Source MP4 exists at `<cwd>/generated/gifs/<date>/_source/<slug>-vNN-source.mp4`
3. Output directory `<cwd>/generated/gifs/<date>/` exists (mkdir -p first)
4. GIF parameters resolved from preset + intent: `fps`, `width`, `colors`, `dither`

---

## Pass 1 — palette generation

```bash
# Generate optimized palette from the source clip
ffmpeg -i <source>.mp4 \
  -vf "fps=<fps>,scale=<width>:-1:flags=lanczos,palettegen=max_colors=<colors>" \
  <slug>-palette.png
```

**What this does:**
- `fps=<fps>` downsamples the source frame rate to the GIF target (10 default)
- `scale=<width>:-1:flags=lanczos` resizes to the GIF target width, height auto-computed (preserves aspect), Lanczos resampling for clean downscaling
- `palettegen=max_colors=<colors>` analyzes all sampled frames and produces an optimized 256-or-fewer color palette PNG

**Output:** an intermediate PNG containing the palette.

---

## Pass 2 — apply palette with dithering

```bash
# Apply palette to source with dither, output GIF
ffmpeg -i <source>.mp4 -i <slug>-palette.png \
  -lavfi "fps=<fps>,scale=<width>:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=<dither>:bayer_scale=5" \
  <slug>-vNN.gif
```

**What this does:**
- Reads the source MP4 (`-i <source>.mp4`) AND the palette PNG (`-i <slug>-palette.png`)
- `fps=<fps>,scale=<width>:-1:flags=lanczos` re-applies the same downsample + scale (must match pass 1 exactly for clean palette mapping)
- `[x][1:v]paletteuse=dither=<dither>` uses the palette (input #2, the PNG) on the rescaled source (label `[x]`)
- `bayer_scale=5` controls the bayer ordered-dither pattern size (5 is balanced — lower = more visible pattern, higher = closer to no-dither posterization)

**Output:** the final GIF.

---

## Default substitutions

For most GIFs, substitute these values:

| Variable | Default value |
|---|---|
| `<fps>` | `10` |
| `<width>` | `480` |
| `<colors>` | `64` |
| `<dither>` | `bayer` |

---

## Photographic variant

For photographic intent (cinematic, realistic, natural motion), swap dither and increase color budget:

| Variable | Photographic value |
|---|---|
| `<colors>` | `128` |
| `<dither>` | `floyd_steinberg` |

`floyd_steinberg` is error-diffusion dithering — smoother on gradients, skin tones, and sky transitions. Larger output file, but no visible bayer grid pattern.

When using `floyd_steinberg`, **omit `bayer_scale=5`** (it's a bayer-only parameter):

```bash
# Photographic variant — paletteuse without bayer_scale
ffmpeg -i <source>.mp4 -i <slug>-palette.png \
  -lavfi "fps=<fps>,scale=<width>:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=floyd_steinberg" \
  <slug>-vNN.gif
```

---

## Trim variant — for GIFs shorter than the source

If the user wants a GIF shorter than the source MP4 duration (e.g., 3s GIF from a 5s source):

**Pass 1 with trim:**
```bash
# Generate palette from a trimmed segment of the source
ffmpeg -i <source>.mp4 -t <seconds> \
  -vf "fps=<fps>,scale=<width>:-1:flags=lanczos,palettegen=max_colors=<colors>" \
  <slug>-palette.png
```

**Pass 2 with trim:**
```bash
# Apply palette to the trimmed segment
ffmpeg -i <source>.mp4 -t <seconds> -i <slug>-palette.png \
  -lavfi "fps=<fps>,scale=<width>:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=<dither>:bayer_scale=5" \
  <slug>-vNN.gif
```

`-t <seconds>` must come **after** `-i <source>.mp4` and **before** the next input. Apply the same `-t` value in both passes so the palette matches the trimmed content.

The full-length source MP4 stays in `_source/` so the user can re-encode at a different trim length later without paying for another fal generation.

---

## Loop behavior

GIF default is infinite loop — no flag needed.

To loop a specific number of times, add `-loop <N>` in pass 2 after the input but before `-lavfi`:

```bash
# Loop the GIF 3 times then stop
ffmpeg -i <source>.mp4 -i <slug>-palette.png -loop 3 \
  -lavfi "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" \
  <slug>-vNN.gif
```

`-loop 0` is infinite (the default). `-loop -1` plays once with no loop.

---

## Discard intermediate palette

After pass 2 succeeds, the intermediate palette PNG can be deleted:

```bash
# Remove the palette after the GIF is written
rm <slug>-palette.png
```

If you want to keep it for re-encoding at different settings (different colors / dither without re-running pass 1), move it to `_source/`:

```bash
# Keep palette in _source/ for future re-encoding
mv <slug>-palette.png _source/<slug>-palette.png
```

For v1, gif-maker discards the palette after pass 2 (less disk usage; user can re-run gif-maker on the source MP4 if they want a different palette).

---

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `palettegen: too few frames` | Source MP4 is shorter than ~1 second | Increase source duration or check that fal returned a valid clip |
| `paletteuse: width mismatch` | `scale` parameters differ between pass 1 and pass 2 | Use the same `fps`, `width`, and scaling flags in both passes |
| `ffmpeg: command not found` | ffmpeg not installed | `brew install ffmpeg` (macOS) · `apt install ffmpeg` (Debian) · `choco install ffmpeg` (Windows) |
| `Invalid argument` on `bayer_scale` with `floyd_steinberg` | bayer_scale is a bayer-only param | Omit `bayer_scale=5` when using `dither=floyd_steinberg` |
| GIF is huge (~50MB+) | Color budget too high or width too wide | Lower `<colors>` (try 64 or 32) or `<width>` (try 320) |
| GIF stutters visibly | Source fps and target fps differ a lot, fps too low | Try fps=12 or fps=15 instead of 10 |
| GIF colors look wrong on dark backgrounds | Dither pattern visible on dark areas | Try `dither=floyd_steinberg` instead of `bayer` |
