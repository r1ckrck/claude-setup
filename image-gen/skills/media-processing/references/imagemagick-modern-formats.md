# ImageMagick Modern Formats

AVIF, HEIC, animated WebP, animated PNG (APNG) — modern image codecs for better compression and animation. Each requires specific ImageMagick delegates and minimum versions.

## Verify Your Build

Before encoding, confirm your ImageMagick build supports the format.

```bash
# List all supported formats
magick -list format

# Check specific modern formats
magick -list format | grep -E 'AVIF|HEIC|WEBP|APNG'

# Check delegate libraries (the underlying codec libs)
magick -list delegate | grep -E 'heic|avif|webp'

# ImageMagick version (need ≥7.1 for AVIF/HEIC)
magick -version
```

**Minimum versions:**
- AVIF: ImageMagick ≥7.1, libheif ≥1.12 with libaom
- HEIC: ImageMagick ≥7.0, libheif ≥1.12
- Animated WebP: ImageMagick ≥7.0
- APNG: ImageMagick ≥6.9

If a format is missing, reinstall ImageMagick with delegates: `brew reinstall imagemagick` (modern Homebrew enables AVIF/HEIC/WebP by default).

## AVIF

Best compression among image codecs; supports 12-bit color, HDR, and alpha.

```bash
# JPEG to AVIF (default quality)
magick input.jpg output.avif

# AVIF with quality control (0-100, higher = larger file, default 75)
magick input.jpg -quality 60 output.avif

# Lossless AVIF
magick input.png -quality 100 -define avif:lossless=true output.avif

# AVIF with specific encoder speed (0-10, lower = slower & smaller, default 6)
magick input.jpg -define avif:speed=2 -quality 60 output.avif

# Strip metadata while encoding (privacy + smaller file)
magick input.jpg -strip -quality 60 output.avif

# AVIF to JPEG (decode)
magick input.avif output.jpg
```

## HEIC

Apple's preferred image format; smaller than JPEG at equivalent quality.

```bash
# JPEG to HEIC
magick input.jpg output.heic

# HEIC with quality
magick input.jpg -quality 80 output.heic

# Read HEIC, write to JPEG (decode)
magick input.heic output.jpg

# HEIC to PNG (decode + lossless)
magick input.heic output.png

# Batch convert HEIC folder to JPEG
mogrify -format jpg -quality 90 -path ./jpegs *.heic
```

## Animated WebP

Smaller alternative to GIF, supports millions of colors and alpha.

```bash
# Build animated WebP from frame sequence (100ms per frame, infinite loop)
magick -delay 10 -loop 0 frame_*.png animated.webp

# Animated WebP with quality
magick -delay 10 -loop 0 -quality 75 frame_*.png animated.webp

# Faster playback (50ms per frame = 20fps)
magick -delay 5 -loop 0 frame_*.png animated.webp

# Single loop (play once)
magick -delay 10 -loop 1 frame_*.png animated.webp

# GIF to animated WebP (smaller file)
magick input.gif output.webp

# Animated WebP to GIF (for compatibility)
magick input.webp output.gif

# Lossless animated WebP
magick -delay 10 -loop 0 -define webp:lossless=true frame_*.png animated.webp
```

## APNG (Animated PNG)

Browser-supported lossless animation. Larger files than WebP/GIF, but no quality loss.

```bash
# Build APNG from frame sequence
magick -delay 10 -loop 0 frame_*.png animated.png

# Force APNG output (some IM builds need explicit PNG: prefix)
magick -delay 10 -loop 0 frame_*.png APNG:animated.png

# APNG with optimization (smaller file via inter-frame prediction)
magick -delay 10 -loop 0 frame_*.png -layers OptimizeFrame animated.png

# GIF to APNG (lossless)
magick input.gif APNG:animated.png

# APNG to GIF (lossy — loses color depth)
magick animated.png output.gif
```

## ICC Profile Preservation

Modern formats can carry ICC color profiles. Preserve them across conversion or strip explicitly.

```bash
# Preserve ICC during conversion (default if profile present)
magick input.jpg output.avif

# Inspect embedded profile
magick identify -format "%[colorspace] %[profile:icc]\n" input.jpg

# Strip ICC explicitly
magick input.jpg -strip output.avif

# Strip everything except ICC
magick input.jpg -define preserve-properties=icc -strip output.avif

# Convert from one profile to another (e.g., AdobeRGB to sRGB)
magick input.jpg -profile sRGB.icc output.jpg

# Embed a specific profile
magick input.png -profile /System/Library/ColorSync/Profiles/sRGB Profile.icc output.jpg
```

## Format Comparison

For one image, encode in multiple formats and compare sizes.

```bash
# Encode same image in multiple formats at quality 75
magick input.png -quality 75 output.jpg
magick input.png -quality 75 output.webp
magick input.png -quality 75 output.heic
magick input.png -quality 75 output.avif

# Compare file sizes
ls -l output.{jpg,webp,heic,avif} | awk '{print $5, $NF}' | sort -n
```

## Common Recipes

### Modernize JPEG Folder To AVIF

```bash
# Batch convert all JPEGs to AVIF at quality 60, preserve ICC
mkdir -p avif
for f in *.jpg; do
  magick "$f" -quality 60 "avif/${f%.jpg}.avif"
done
```

### Create Animated WebP From Video Frames

```bash
# 1. Extract video frames with ffmpeg
ffmpeg -i video.mp4 -vf "fps=15,scale=480:-1" frame_%03d.png

# 2. Build animated WebP
magick -delay 7 -loop 0 -quality 80 frame_*.png animated.webp

# 3. Cleanup intermediates
rm frame_*.png
```

### iPhone HEIC Photos To Universal JPEG

```bash
# Convert all HEIC in folder to JPEG, preserve EXIF + orientation
mogrify -format jpg -quality 90 -path ./jpegs *.heic
```

### Lossless Animated PNG From Frame Sequence

```bash
magick -delay 10 -loop 0 frame_*.png -layers OptimizeFrame animated.png
```

### Verify A File Has An ICC Profile Embedded

```bash
# Returns "icc" if present, empty string otherwise
magick identify -format "%[profile:icc]\n" input.avif
```

### Strip All Metadata But Keep ICC + Orientation Across A Folder

```bash
# Per-image preservation pattern (uses exiftool, not IM — see ffmpeg-metadata.md)
exiftool -all= -tagsfromfile @ -Orientation -ICC_Profile -overwrite_original *.jpg
```

### Test Multiple Quality Levels At Once

```bash
# Encode same source at multiple AVIF qualities for comparison
for q in 30 50 70 90; do
  magick input.png -quality $q "test_q${q}.avif"
done
ls -lh test_q*.avif
```

### Resize During Modern-Format Conversion

```bash
# Resize and convert to AVIF in one pass
magick input.jpg -resize 1920x -quality 60 output.avif

# Resize and convert to HEIC
magick input.jpg -resize 1920x -quality 80 output.heic

# Generate responsive set in modern format
for w in 480 768 1280 1920; do
  magick input.jpg -resize ${w}x -quality 60 "output-${w}w.avif"
done
```

### Animated Format Conversion Chain

```bash
# Source GIF → animated WebP → MP4 (chain through ffmpeg)
magick input.gif -quality 75 animated.webp
ffmpeg -i animated.webp -c:v libx264 -pix_fmt yuv420p -movflags +faststart output.mp4

# Source PNG sequence → APNG → GIF
magick -delay 10 -loop 0 frame_*.png APNG:animated.png
magick animated.png -fuzz 5% -layers Optimize animated.gif
```

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `no decode delegate for this image format 'HEIC'` | ImageMagick missing libheif | `brew reinstall imagemagick` (modern Homebrew bundles libheif) |
| `unable to open module file ... 'IM_MOD_RL_AVIF_.dll'` (Windows) | AVIF delegate missing | Install ImageMagick build with libheif + libaom |
| AVIF output much larger than expected | Lossless mode active by default in some builds | Add `-quality 60` explicitly |
| HEIC encode succeeds but reads as black | Encoding 16-bit source without depth conversion | Add `-depth 8` before output |
| Animated WebP plays once and stops | Default loop is `0` (infinite) but explicit `-loop 1` was set | Use `-loop 0` for infinite loop |
