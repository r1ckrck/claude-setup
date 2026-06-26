---
name: media-processing
description: Process multimedia files with FFmpeg and ImageMagick. Use when converting between video / audio / image formats, encoding with specific codecs (H.264, H.265, VP9, AV1, ProRes, DNxHR), resizing or cropping images, extracting or mixing audio, applying filters and effects, burning in or extracting subtitles, applying LUTs and color grading, tone-mapping HDR to SDR, converting to modern formats (AVIF, HEIC, animated WebP, APNG), two-pass encoding with GOP / profile / codec-specific control, compositing videos (picture-in-picture, hstack, vstack, grid, chromakey, xfade transitions, concat), audio mastering (EBU R128 loudnorm, silence detection, reverb, chorus, audio crossfade), reading or writing metadata (EXIF, ID3, IPTC, XMP, GPS, copyright, chapters), stripping metadata for privacy, scene detection, histogram and signalstats analysis, motion estimation, blackdetect / freezedetect QC, generating thumbnails, batch processing, hardware-accelerated encoding (NVENC / QuickSync / VideoToolbox), or implementing media-processing pipelines. Supports 100+ formats and complex filtergraphs.
---

# Media Processing Skill

Process video, audio, and images using FFmpeg and ImageMagick command-line tools for conversion, optimization, and manipulation tasks.

This skill is a **command-reference**: each operation is a bash recipe. It does not generate AI media (see sibling skill `fal-image` for that), and it does not give styling or aesthetic guidance — only the commands needed to operate FFmpeg and ImageMagick. The skill is self-contained — copy `.claude/skills/media-processing/` into any project to use it. No external documentation references; everything the skill needs is in this folder. Sibling skills (`fal-image`, future `fal-video` and `gif-maker`) may chain to this skill for post-processing — for example, `gif-maker` calls `fal-video` to produce a source clip, then routes the file here for ffmpeg-based palette generation and dithering.

## When to Use This Skill

Use when:
- Converting media formats (video, audio, images)
- Encoding video with codecs (H.264, H.265, VP9, AV1)
- Processing images (resize, crop, effects, watermarks)
- Extracting audio from video
- Generating thumbnails and previews
- Batch processing media files
- Optimizing file sizes and quality
- Applying filters and effects
- Creating composite images or videos

## Tool Selection Guide

### FFmpeg: Video/Audio Processing
Use FFmpeg for:
- Video encoding, conversion, transcoding
- Audio extraction, conversion, mixing
- Video filters (scale, crop, rotate, overlay)
- Hardware-accelerated encoding
- Media file inspection (ffprobe)
- Frame extraction, concatenation
- Codec selection and optimization

### ImageMagick: Image Processing
Use ImageMagick for:
- Image format conversion (PNG, JPEG, WebP, GIF)
- Resizing, cropping, transformations
- Batch image processing (mogrify)
- Visual effects (blur, sharpen, sepia)
- Text overlays and watermarks
- Image composition and montages
- Color adjustments, filters
- Thumbnail generation

### Decision Matrix

| Task | Tool | Why |
|------|------|-----|
| Video encoding | FFmpeg | Native video codec support |
| Audio extraction | FFmpeg | Direct stream manipulation |
| Image resize | ImageMagick | Optimized for still images |
| Batch images | ImageMagick | mogrify for in-place edits |
| Video thumbnails | FFmpeg | Frame extraction built-in |
| GIF creation | FFmpeg or ImageMagick | FFmpeg for video source, ImageMagick for images |
| Image effects | ImageMagick | Rich filter library |
| Burn-in subtitles | FFmpeg | Native libass styling |
| Extract / convert subtitles | FFmpeg | Stream mapping built-in |
| LUT color grading | FFmpeg | `lut3d` filter, `.cube` support |
| HDR tone-mapping | FFmpeg | `zscale` + `tonemap` |
| AVIF / HEIC encode | ImageMagick | libheif + libaom delegates |
| ProRes / DNxHR | FFmpeg | Native pro-codec support |
| Animated WebP / APNG | ImageMagick | Frame-sequence assembly |
| Strip metadata | FFmpeg or exiftool | Privacy / web optimization |
| Scene detection | FFmpeg | `select=scene` filter |
| Loudness mastering | FFmpeg | EBU R128 `loudnorm` |

## Installation

### macOS
```bash
brew install ffmpeg imagemagick
```

### Ubuntu/Debian
```bash
sudo apt-get install ffmpeg imagemagick
```

### Windows
```bash
# Using winget
winget install ffmpeg
winget install ImageMagick.ImageMagick

# Or download binaries
# FFmpeg: https://ffmpeg.org/download.html
# ImageMagick: https://imagemagick.org/script/download.php
```

### Verify Installation
```bash
ffmpeg -version
ffprobe -version
magick -version
# or
convert -version
```

## Pre-Flight (For Modern Capabilities)

Before using subtitles, color grading, modern formats, audio effects, or metadata recipes, verify your build supports them.

```bash
# Subtitle burn-in needs libass
ffmpeg -filters 2>/dev/null | grep -E 'subtitles|ass'

# AVIF / HEIC need libheif (+ libaom for AVIF)
magick -list format | grep -E 'AVIF|HEIC'

# ProRes / DNxHR
ffmpeg -encoders 2>/dev/null | grep -E 'prores|dnxhd'

# LUTs (lut3d filter)
ffmpeg -filters 2>/dev/null | grep lut3d

# EBU R128 loudness
ffmpeg -filters 2>/dev/null | grep loudnorm

# exiftool (image EXIF / IPTC / XMP — ffmpeg cannot write these)
which exiftool || echo "Install: brew install exiftool"

# SoX (better-quality audio effects than ffmpeg native)
which sox || echo "Install: brew install sox"
```

**Minimum versions:**
- ffmpeg ≥5.0 (AV1 SVT, modern tone-mapping)
- ImageMagick ≥7.1 (HEIC + AVIF)
- libheif ≥1.12
- exiftool ≥12.0

If a check fails, reinstall the missing tool (modern Homebrew bundles delegates by default): `brew install ffmpeg imagemagick libheif exiftool sox`.

## Quick Start Examples

### Video Conversion
```bash
# Convert format (copy streams, fast)
ffmpeg -i input.mkv -c copy output.mp4

# Re-encode with H.264
ffmpeg -i input.avi -c:v libx264 -crf 22 -c:a aac output.mp4

# Resize video to 720p
ffmpeg -i input.mp4 -vf scale=-1:720 -c:a copy output.mp4
```

### Audio Extraction
```bash
# Extract audio (no re-encoding)
ffmpeg -i video.mp4 -vn -c:a copy audio.m4a

# Convert to MP3
ffmpeg -i video.mp4 -vn -q:a 0 audio.mp3
```

### Image Processing
```bash
# Convert format
magick input.png output.jpg

# Resize maintaining aspect ratio
magick input.jpg -resize 800x600 output.jpg

# Create square thumbnail
magick input.jpg -resize 200x200^ -gravity center -extent 200x200 thumb.jpg
```

### Batch Image Resize
```bash
# Resize all JPEGs to 800px width
mogrify -resize 800x -quality 85 *.jpg

# Output to separate directory
mogrify -path ./output -resize 800x600 *.jpg
```

### Video Thumbnail
```bash
# Extract frame at 5 seconds
ffmpeg -ss 00:00:05 -i video.mp4 -vframes 1 -vf scale=320:-1 thumb.jpg
```

### Image Watermark
```bash
# Add watermark to corner
magick input.jpg watermark.png -gravity southeast \
  -geometry +10+10 -composite output.jpg
```

### Burn-In Subtitles
```bash
ffmpeg -i video.mp4 -vf "subtitles=subs.srt" -c:a copy output.mp4
```

### Apply LUT (Color Grade)
```bash
ffmpeg -i input.mp4 -vf "lut3d=cinematic.cube" -c:a copy output.mp4
```

### Convert To AVIF
```bash
magick input.jpg -quality 60 output.avif
```

### Convert To HEIC
```bash
magick input.jpg -quality 80 output.heic
```

### Two-Pass Encoding (Target File Size)
```bash
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac output.mp4
```

### Concat Without Re-encoding
```bash
# list.txt contains lines like: file 'clip1.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### Side-By-Side Comparison
```bash
ffmpeg -i left.mp4 -i right.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2[v]" \
  -map "[v]" -c:v libx264 compare.mp4
```

### Strip Metadata For Privacy
```bash
# Video / audio
ffmpeg -i input.mp4 -map_metadata -1 -c copy clean.mp4
# Image (preserve orientation + ICC)
exiftool -all= -tagsfromfile @ -Orientation -ICC_Profile -overwrite_original photo.jpg
```

### Loudness Normalize (EBU R128)
```bash
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1:LRA=11" output.mp3
```

### Scene Detect + Extract Thumbnails
```bash
ffmpeg -i video.mp4 -vf "select='gt(scene,0.4)',scale=320:-1" -vsync vfr scene_%03d.jpg
```

## Common Workflows

### Optimize Video for Web
```bash
# H.264 with good compression
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  output.mp4
```

### Create Responsive Images
```bash
# Generate multiple sizes
for size in 320 640 1024 1920; do
  magick input.jpg -resize ${size}x -quality 85 "output-${size}w.jpg"
done
```

### Extract Video Segment
```bash
# From 1:30 to 3:00 (re-encode for precision)
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:00 \
  -c:v libx264 -c:a aac output.mp4
```

### Batch Image Optimization
```bash
# Convert PNG to optimized JPEG
mogrify -path ./optimized -format jpg -quality 85 -strip *.png
```

### Video GIF Creation
```bash
# High quality GIF with palette
ffmpeg -i input.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

### Image Blur Effect
```bash
# Gaussian blur
magick input.jpg -gaussian-blur 0x8 output.jpg
```

### Subtitled Clip For Social
```bash
# Translate subs externally, then burn in with consistent style
ffmpeg -i clip.mp4 -vf "subtitles=translated.srt:force_style='Fontname=Helvetica Bold,Fontsize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=60'" -c:v libx264 -crf 20 -c:a copy social.mp4
```

### Color-Grade Pipeline
```bash
# LUT + curves + saturation + vignette in one chain
ffmpeg -i input.mp4 -vf \
  "lut3d=cinematic.cube,curves=preset=medium_contrast,eq=saturation=1.05,vignette=PI/5" \
  -c:v libx264 -crf 20 -c:a copy graded.mp4
```

### Greenscreen Composite
```bash
ffmpeg -stream_loop -1 -i background.mp4 -i fg_greenscreen.mp4 \
  -filter_complex "[1:v]chromakey=0x00FF00:0.1:0.05[ckout];[0:v][ckout]overlay[v]" \
  -map "[v]" -map 1:a -shortest -c:v libx264 output.mp4
```

### Multi-Clip Montage With xfade + Audio Crossfade
```bash
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex \
    "[0:v][1:v]xfade=fade:1:5[v01]; \
     [v01][2:v]xfade=fade:1:11[v]; \
     [0:a][1:a]acrossfade=d=1[a01]; \
     [a01][2:a]acrossfade=d=1[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -c:a aac montage.mp4
```

### Podcast Audio Mastering
```bash
# Two-pass loudnorm to -16 LUFS, encode to MP3 192k
ffmpeg -i raw.wav -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | tail -n 12
# (read measured values, then apply with measured_I / measured_TP / measured_LRA / measured_thresh / offset)
ffmpeg -i raw.wav -af "loudnorm=I=-16:TP=-1:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<th>:offset=<o>:linear=true" -c:a libmp3lame -b:a 192k podcast.mp3
```

### Modern Format Batch (Folder Of JPEGs → AVIF)
```bash
mkdir -p avif
for f in *.jpg; do
  magick "$f" -quality 60 "avif/${f%.jpg}.avif"
done
```

## Advanced Techniques

### Multi-Pass Video Encoding
```bash
# Pass 1 (analysis)
ffmpeg -y -i input.mkv -c:v libx264 -b:v 2600k -pass 1 -an -f null /dev/null

# Pass 2 (encoding)
ffmpeg -i input.mkv -c:v libx264 -b:v 2600k -pass 2 -c:a aac output.mp4
```

### Hardware-Accelerated Encoding
```bash
# NVIDIA NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset fast -crf 22 output.mp4

# Intel QuickSync
ffmpeg -hwaccel qsv -c:v h264_qsv -i input.mp4 -c:v h264_qsv output.mp4
```

### Complex Image Pipeline
```bash
# Resize, crop, border, adjust
magick input.jpg \
  -resize 1000x1000^ \
  -gravity center \
  -crop 1000x1000+0+0 +repage \
  -bordercolor black -border 5x5 \
  -brightness-contrast 5x10 \
  -quality 90 \
  output.jpg
```

### Video Filter Chains
```bash
# Scale, denoise, watermark
ffmpeg -i video.mp4 -i logo.png \
  -filter_complex "[0:v]scale=1280:720,hqdn3d[v];[v][1:v]overlay=10:10" \
  -c:a copy output.mp4
```

### Animated GIF from Images
```bash
# Create with delay
magick -delay 100 -loop 0 frame*.png animated.gif

# Optimize size
magick animated.gif -fuzz 5% -layers Optimize optimized.gif
```

## Media Analysis

### Inspect Video Properties
```bash
# Detailed JSON output
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Get resolution
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height \
  -of csv=s=x:p=0 input.mp4
```

### Image Information
```bash
# Basic info
identify image.jpg

# Detailed format
identify -verbose image.jpg

# Custom format
identify -format "%f: %wx%h %b\n" image.jpg
```

## Performance Tips

1. **Use CRF for quality control** - Better than bitrate for video
2. **Copy streams when possible** - Avoid re-encoding with `-c copy`
3. **Hardware acceleration** - GPU encoding 5-10x faster
4. **Appropriate presets** - Balance speed vs compression
5. **Batch with mogrify** - In-place image processing
6. **Strip metadata** - Reduce file size with `-strip`
7. **Progressive JPEG** - Better web loading with `-interlace Plane`
8. **Limit memory** - Prevent crashes on large batches
9. **Test on samples** - Verify settings before batch
10. **Parallel processing** - Use GNU Parallel for multiple files

## Reference Documentation

Detailed guides in `references/`:

- **ffmpeg-encoding.md** - Video/audio codecs, CRF/bitrate, hardware acceleration, two-pass VBR/CBR, GOP, profiles & levels, x264/x265 advanced opts, tune options, interactions
- **ffmpeg-filters.md** - Video/audio filters (scale, crop, overlay, denoise, eq, fade, drawtext, etc.). Composition recipes split out to ffmpeg-composition.md
- **ffmpeg-color.md** - LUT (`lut3d`, `.cube`), curves, HDR tone-mapping, colorspace conversion, pixel format & range
- **ffmpeg-subtitles.md** - Burn-in, soft-mux, extract, format conversion (SRT/ASS/VTT), styling, sync
- **ffmpeg-composition.md** - hstack/vstack/xstack grids, picture-in-picture, chromakey/colorkey, xfade transitions, concat (demuxer vs filter), slideshow, montage
- **ffmpeg-audio-effects.md** - Silence detect/insert, reverb/chorus/flanger/phaser, dynaudnorm, two-pass loudnorm, audio crossfade & concat. SoX-better callouts
- **ffmpeg-metadata.md** - Read/write metadata, strip for privacy, GPS, chapters, ID3 tags. exiftool callout for image EXIF/IPTC/XMP
- **ffmpeg-analysis.md** - Scene detection, histogram, signalstats, motion estimation, blackdetect/freezedetect, ffprobe deep usage, frame-md5, PSNR/SSIM
- **imagemagick-editing.md** - Format conversion, effects, transformations, ICC profiles
- **imagemagick-batch.md** - Batch processing, mogrify, parallel operations
- **imagemagick-modern-formats.md** - AVIF, HEIC, animated WebP, APNG, ICC profile preservation, version checks
- **format-compatibility.md** - Format support, codec recommendations, minimum versions per format

*For batch or multi-step workflows, a short Python wrapper around the ffmpeg / ImageMagick commands above can be cleaner than long bash chains. Optional — most tasks don't need it.*

## Common Parameters

### FFmpeg Video
- `-c:v` - Video codec (libx264, libx265, libvpx-vp9)
- `-crf` - Quality (0-51, lower=better, 23=default)
- `-preset` - Speed/compression (ultrafast to veryslow)
- `-b:v` - Video bitrate (e.g., 2M, 2500k)
- `-vf` - Video filters

### FFmpeg Audio
- `-c:a` - Audio codec (aac, mp3, opus)
- `-b:a` - Audio bitrate (e.g., 128k, 192k)
- `-ar` - Sample rate (44100, 48000)

### ImageMagick Geometry
- `800x600` - Fit within (maintains aspect)
- `800x600!` - Force exact size
- `800x600^` - Fill (may crop)
- `800x` - Width only
- `x600` - Height only
- `50%` - Scale percentage

### FFmpeg Subtitles
- `-c:s` - Subtitle codec (`mov_text` for MP4, `srt` for MKV, `webvtt` for WebVTT)
- `force_style` - Inline ASS-style override (e.g., `Fontname=`, `Fontsize=`, `PrimaryColour=`, `Alignment=`)
- `-itsoffset` - Time offset for sync
- `:fontsdir` - Custom font directory for the `subtitles=` filter

### FFmpeg Color
- `-color_primaries` - Color primaries tag (`bt709`, `bt2020`, `bt601-6-625`)
- `-color_trc` - Transfer function (`bt709`, `smpte2084`, `arib-std-b67`)
- `-colorspace` - Matrix coefficients (`bt709`, `bt2020nc`, `bt601`)
- `-color_range` - Range (`tv` = limited 16-235, `pc` = full 0-255)
- `-pix_fmt` - Pixel format (`yuv420p`, `yuv422p10le`, `yuv444p`)

### FFmpeg Metadata
- `-metadata` - Set container-level tag (`-metadata title="..."`)
- `-metadata:s:<type>:<idx>` - Set per-stream tag (`-metadata:s:a:0 language=eng`)
- `-map_metadata -1` - Strip all metadata
- `-fflags +bitexact` - Strip encoder watermark

## Troubleshooting

**FFmpeg "Unknown encoder"**
```bash
# Check available encoders
ffmpeg -encoders | grep h264

# Install codec libraries
sudo apt-get install libx264-dev libx265-dev
```

**ImageMagick "not authorized"**
```bash
# Edit policy file
sudo nano /etc/ImageMagick-7/policy.xml
# Change <policy domain="coder" rights="none" pattern="PDF" />
# to <policy domain="coder" rights="read|write" pattern="PDF" />
```

**Memory errors**
```bash
# Limit memory usage
ffmpeg -threads 4 input.mp4 output.mp4
magick -limit memory 2GB -limit map 4GB input.jpg output.jpg
```

**Subtitle font not found**
```bash
# Linux: fontconfig can't find a font when burning in subtitles
# Either supply fontsdir, or force a font fontconfig has
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:fontsdir=/usr/share/fonts" output.mp4
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='Fontname=DejaVu Sans'" output.mp4
```

**HEIC: no decode delegate**
```bash
# ImageMagick missing libheif
brew reinstall imagemagick   # macOS
sudo apt install libheif-dev # Debian/Ubuntu, then rebuild IM if from source

# Verify
magick -list format | grep HEIC
```

**Two-pass log not found**
```bash
# Pass 1 wasn't run, was killed early, or used a different passlogfile
# Use explicit passlogfile to keep them paired
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -passlogfile /tmp/job1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -passlogfile /tmp/job1 -c:a aac output.mp4
```

## Resources

- FFmpeg: https://ffmpeg.org/documentation.html
- FFmpeg Wiki: https://trac.ffmpeg.org/
- ImageMagick: https://imagemagick.org/
- ImageMagick Usage: https://imagemagick.org/Usage/
