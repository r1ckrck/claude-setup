# FFmpeg Color

Apply LUTs, curves, color-grade pipelines, tone-map HDR to SDR, convert colorspaces, and tag pixel format / range. For finishing-grade work, use a dedicated grading tool (DaVinci Resolve, Baselight). This file covers the ffmpeg path.

> **BYO LUT.** This skill does not ship `.cube` files (license risk). Use your own, or generate a test identity LUT (recipe below) to verify the pipeline works.

## LUT Application

Apply a 3D color lookup table from a `.cube` file.

```bash
# Apply LUT to entire video
ffmpeg -i input.mp4 -vf "lut3d=cinematic.cube" -c:a copy output.mp4

# Apply LUT with specific interpolation (tetrahedral = highest quality)
ffmpeg -i input.mp4 -vf "lut3d=cinematic.cube:interp=tetrahedral" output.mp4

# Mix LUT effect with original (50% strength via blend)
ffmpeg -i input.mp4 -filter_complex "[0:v]split[a][b];[b]lut3d=cinematic.cube[graded];[a][graded]blend=all_mode=normal:all_opacity=0.5" output.mp4

# Apply 1D LUT (.cube 1D format, used for tone mapping per channel)
ffmpeg -i input.mp4 -vf "lut1d=tone.cube" output.mp4
```

### Generate Identity LUT (Test File)

A 17-point identity LUT — applies no change. Use to verify the LUT pipeline before sourcing real LUTs.

```bash
# Create identity LUT in current directory
{
  echo 'TITLE "Identity 17"'
  echo 'LUT_3D_SIZE 17'
  for r in $(seq 0 16); do
    for g in $(seq 0 16); do
      for b in $(seq 0 16); do
        printf "%.6f %.6f %.6f\n" $(echo "scale=6; $r/16" | bc) $(echo "scale=6; $g/16" | bc) $(echo "scale=6; $b/16" | bc)
      done
    done
  done
} > identity.cube

# Verify by applying — output should match input exactly
ffmpeg -i input.mp4 -vf "lut3d=identity.cube" -c:a copy verify.mp4
```

## Curves

Apply tonal curves per channel (RGB or luma). Useful for matching a look without a LUT.

```bash
# Built-in preset (vintage, lighter, darker, increase_contrast, decrease_contrast, negative, color_negative, cross_process, medium_contrast, strong_contrast, linear_contrast)
ffmpeg -i input.mp4 -vf "curves=preset=vintage" -c:a copy output.mp4

# Strong contrast preset
ffmpeg -i input.mp4 -vf "curves=preset=strong_contrast" output.mp4

# Custom curve via control points (lift shadows, crush highlights)
ffmpeg -i input.mp4 -vf "curves=master='0/0.1 0.5/0.5 1/0.9'" output.mp4

# Per-channel curve (warm tones — lift R, lift midtone B)
ffmpeg -i input.mp4 -vf "curves=red='0/0 0.5/0.6 1/1':blue='0/0 0.5/0.45 1/1'" output.mp4

# Load curves from photoshop .acv file
ffmpeg -i input.mp4 -vf "curves=psfile=mycurve.acv" output.mp4
```

## Colorspace Conversion

Convert between color spaces (Rec.709 SDR, Rec.2020 HDR/UHD, Rec.601 SD).

```bash
# 709 to 2020 (SDR HD to UHD)
ffmpeg -i input.mp4 -vf "colorspace=bt2020:iall=bt709:fast=1" -c:a copy output.mp4

# 2020 to 709 (UHD to HD — pair with tone-mapping for HDR)
ffmpeg -i input.mp4 -vf "colorspace=bt709:iall=bt2020" output.mp4

# 601 (SD) to 709 (HD)
ffmpeg -i input.mp4 -vf "colorspace=bt709:iall=bt601-6-625" output.mp4

# Force colorspace tagging without conversion (fix mistagged source)
ffmpeg -i input.mp4 -c:v libx264 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a copy output.mp4
```

## HDR Tone-Mapping

Convert HDR (HDR10 / HLG) to SDR using `zscale` + `tonemap`.

```bash
# HDR10 (PQ) to SDR Rec.709
ffmpeg -i hdr.mp4 -vf \
  "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a copy sdr.mp4

# HDR10 to SDR with reinhard tone mapping (softer)
ffmpeg -i hdr.mp4 -vf \
  "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=reinhard:param=0.5,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 18 sdr.mp4

# HLG to SDR
ffmpeg -i hlg.mp4 -vf \
  "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 18 sdr.mp4

# Inverse (SDR to HDR-tagged — fake HDR, only fixes container metadata)
ffmpeg -i sdr.mp4 -c:v libx265 -pix_fmt yuv420p10le \
  -color_primaries bt2020 -color_trc smpte2084 -colorspace bt2020nc \
  -x265-params "colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:hdr-opt=1:repeat-headers=1" \
  fake_hdr.mp4
```

**Tone-map operators:** `none`, `linear`, `gamma`, `clip`, `reinhard`, `hable`, `mobius`. Hable and Mobius are the most natural-looking for filmic content.

## Pixel Format & Range

Pixel format = chroma subsampling + bit depth. Range = full (0-255) vs limited/TV (16-235).

```bash
# Convert to 4:2:0 8-bit (universal compatibility)
ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx264 output.mp4

# Convert to 4:2:2 10-bit (broadcast / mezzanine)
ffmpeg -i input.mov -pix_fmt yuv422p10le -c:v libx264 output.mp4

# Convert to 4:4:4 (no chroma subsampling — for graphics / text)
ffmpeg -i input.mov -pix_fmt yuv444p -c:v libx264 output.mp4

# Force full range (PC/RGB)
ffmpeg -i input.mov -vf "scale=in_range=tv:out_range=pc" -pix_fmt yuv420p output.mp4

# Force limited range (TV)
ffmpeg -i input.mov -vf "scale=in_range=pc:out_range=tv" -pix_fmt yuv420p output.mp4

# Set range tag without converting (fix mistagged source)
ffmpeg -i input.mov -c:v libx264 -color_range tv output.mp4
```

## Color Adjustments (Quick)

Lower-level than LUTs/curves — direct value tweaks. Faster for one-off adjustments.

```bash
# Brightness, contrast, saturation, gamma
ffmpeg -i input.mp4 -vf "eq=brightness=0.05:contrast=1.2:saturation=1.1:gamma=0.95" output.mp4

# Hue rotation (degrees) and saturation multiplier
ffmpeg -i input.mp4 -vf "hue=h=15:s=1.2" output.mp4

# Color balance (shadows / midtones / highlights, RGB shift)
ffmpeg -i input.mp4 -vf "colorbalance=rs=.1:gs=-.05:bs=-.1:rm=.05:gm=0:bm=0:rh=-.05:gh=0:bh=.1" output.mp4

# Color levels (clip black/white, gamma)
ffmpeg -i input.mp4 -vf "colorlevels=rimin=0.05:gimin=0.05:bimin=0.05:rimax=0.95:gimax=0.95:bimax=0.95" output.mp4

# Vibrance (saturate less-saturated colors)
ffmpeg -i input.mp4 -vf "vibrance=intensity=0.5" output.mp4
```

## Combined Color-Grade Pipeline

Chain LUT + curves + saturation + vignette in one filter graph.

```bash
ffmpeg -i input.mp4 -vf \
  "lut3d=cinematic.cube,curves=preset=medium_contrast,eq=saturation=1.05,vignette=PI/5" \
  -c:v libx264 -crf 20 -c:a copy graded.mp4
```

## Common Recipes

### Tag Source As Rec.709 (Fix Mistagged File)
```bash
ffmpeg -i input.mp4 -c:v libx264 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a copy fixed.mp4
```

### Apply LUT Then Re-encode For Web
```bash
ffmpeg -i input.mp4 -vf "lut3d=look.cube" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  web.mp4
```

### HDR To SDR + Re-encode
```bash
ffmpeg -i hdr.mp4 -vf \
  "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a copy sdr.mp4
```

### Verify Color Tags
```bash
# Show colorspace, primaries, transfer, range
ffprobe -loglevel error -select_streams v:0 \
  -show_entries stream=color_space,color_primaries,color_transfer,color_range \
  -of default=noprint_wrappers=1 input.mp4
```
