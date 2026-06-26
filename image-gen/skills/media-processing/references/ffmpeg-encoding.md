# FFmpeg Video & Audio Encoding

Complete guide to codec selection, quality optimization, and hardware acceleration.

## Video Codecs

### H.264 (libx264)
Most widely supported codec, excellent compression/quality balance.

**Best for:** Universal compatibility, streaming, web video

**Quality range:** CRF 17-28 (lower = better)

```bash
# High quality
ffmpeg -i input.mkv -c:v libx264 -preset slow -crf 18 -c:a copy output.mp4

# Standard quality (recommended)
ffmpeg -i input.mkv -c:v libx264 -preset medium -crf 23 -c:a copy output.mp4

# Fast encoding
ffmpeg -i input.mkv -c:v libx264 -preset fast -crf 23 -c:a copy output.mp4
```

### H.265/HEVC (libx265)
25-50% better compression than H.264, slower encoding.

**Best for:** 4K video, file size reduction, archival

```bash
# High quality 4K
ffmpeg -i input.mkv -c:v libx265 -preset medium -crf 24 -c:a copy output.mp4

# Balanced quality
ffmpeg -i input.mkv -c:v libx265 -preset fast -crf 26 -c:a copy output.mp4
```

### VP9 (libvpx-vp9)
Royalty-free, WebM format, good for YouTube and open-source projects.

**Best for:** YouTube, Chrome/Firefox, open platforms

```bash
# Quality-based (recommended)
ffmpeg -i input.mkv -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Two-pass for better quality
ffmpeg -i input.mkv -c:v libvpx-vp9 -b:v 2M -pass 1 -an -f null /dev/null
ffmpeg -i input.mkv -c:v libvpx-vp9 -b:v 2M -pass 2 -c:a libopus output.webm
```

### AV1 (libaom-av1, libsvtav1)
Next-generation codec, best compression, very slow encoding.

**Best for:** Future-proofing, maximum compression, low bandwidth

```bash
# Using libaom (slow, highest quality)
ffmpeg -i input.mkv -c:v libaom-av1 -crf 30 -b:v 0 -strict experimental output.mp4

# Using SVT-AV1 (faster)
ffmpeg -i input.mkv -c:v libsvtav1 -crf 30 -preset 5 output.mp4
```

## Audio Codecs

### AAC (Industry Standard)
Best quality for streaming, universal support.

```bash
# High quality
ffmpeg -i input.mp4 -c:a aac -b:a 192k output.mp4

# Standard quality
ffmpeg -i input.mp4 -c:a aac -b:a 128k output.mp4

# Low bitrate
ffmpeg -i input.mp4 -c:a aac -b:a 96k output.mp4
```

### MP3 (libmp3lame)
Universal compatibility, good quality.

```bash
# Variable bitrate (best quality)
ffmpeg -i input.wav -c:a libmp3lame -q:a 0 output.mp3

# Constant bitrate
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3
```

### Opus (libopus)
Best quality at low bitrates, ideal for voice and streaming.

```bash
# Voice (mono)
ffmpeg -i input.mp4 -c:a libopus -b:a 32k -ac 1 output.webm

# Music (stereo)
ffmpeg -i input.mp4 -c:a libopus -b:a 128k output.webm
```

### FLAC (Lossless)
No quality loss, archival quality, larger files.

```bash
# Lossless audio
ffmpeg -i input.wav -c:a flac output.flac

# Extract audio losslessly
ffmpeg -i video.mp4 -c:a flac audio.flac
```

## Quality Optimization

### CRF (Constant Rate Factor)
Best for quality-focused encoding. Single-pass, adjusts bitrate for complexity.

**CRF Scale:**
- 0 = Lossless (huge files)
- 17-18 = Visually lossless
- 20-23 = High quality (recommended)
- 24-28 = Medium quality
- 30+ = Low quality
- 51 = Worst quality

```bash
# Visually lossless
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4

# High quality (recommended)
ffmpeg -i input.mp4 -c:v libx264 -crf 22 -preset medium output.mp4

# Balanced quality/size
ffmpeg -i input.mp4 -c:v libx264 -crf 25 -preset fast output.mp4
```

### Bitrate-Based Encoding
Target specific file size or quality. Two-pass recommended.

```bash
# Calculate target bitrate
# bitrate = (target_size_MB * 8192) / duration_seconds - audio_bitrate

# Two-pass encoding (2600k video, 128k audio)
ffmpeg -y -i input.mkv -c:v libx264 -b:v 2600k -pass 1 -an -f null /dev/null
ffmpeg -i input.mkv -c:v libx264 -b:v 2600k -pass 2 -c:a aac -b:a 128k output.mp4
```

### Presets (Speed vs Compression)
Trade-off between encoding speed and file size.

**Available presets:**
- `ultrafast` - Fastest, largest files
- `superfast`
- `veryfast`
- `faster`
- `fast`
- `medium` - Default balance
- `slow` - Better compression
- `slower`
- `veryslow` - Best compression
- `placebo` - Not recommended (minimal gains)

```bash
# Fast encoding (real-time)
ffmpeg -i input.mp4 -c:v libx264 -preset ultrafast -crf 23 output.mp4

# Balanced
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 22 output.mp4

# Best compression (slow)
ffmpeg -i input.mp4 -c:v libx264 -preset veryslow -crf 20 output.mp4
```

## Hardware Acceleration

### NVIDIA NVENC
5-10x faster encoding, slightly larger files than software encoding.

**Requirements:** NVIDIA GPU (GTX 10xx or newer)

```bash
# H.264 with NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset fast -crf 22 output.mp4

# H.265 with NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v hevc_nvenc -preset slow -crf 24 output.mp4

# Quality levels (instead of CRF)
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset slow -rc vbr -cq 22 output.mp4
```

**NVENC Presets:**
- `default` - Balanced
- `slow` - Better quality
- `medium`
- `fast`
- `hp` - High performance
- `hq` - High quality
- `bd` - Bluray disk
- `ll` - Low latency
- `llhq` - Low latency high quality
- `llhp` - Low latency high performance

### Intel QuickSync (QSV)
Fast hardware encoding on Intel CPUs with integrated graphics.

**Requirements:** Intel CPU with Quick Sync Video support

```bash
# H.264 with QSV
ffmpeg -hwaccel qsv -c:v h264_qsv -i input.mp4 \
  -c:v h264_qsv -preset fast -global_quality 22 output.mp4

# H.265 with QSV
ffmpeg -hwaccel qsv -c:v hevc_qsv -i input.mp4 \
  -c:v hevc_qsv -preset medium -global_quality 24 output.mp4

# Quality levels
ffmpeg -hwaccel qsv -i input.mp4 -c:v h264_qsv -global_quality 20 output.mp4
```

### AMD VCE/VCN
Hardware encoding on AMD GPUs.

**Requirements:** AMD GPU with VCE/VCN support

```bash
# H.264 with AMF
ffmpeg -hwaccel auto -i input.mp4 \
  -c:v h264_amf -quality balanced -rc cqp -qp 22 output.mp4

# H.265 with AMF
ffmpeg -hwaccel auto -i input.mp4 \
  -c:v hevc_amf -quality quality -rc cqp -qp 24 output.mp4
```

### Apple VideoToolbox (macOS)
Hardware encoding on macOS devices.

```bash
# H.264 with VideoToolbox
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 2M output.mp4

# H.265 with VideoToolbox
ffmpeg -i input.mp4 -c:v hevc_videotoolbox -b:v 1.5M output.mp4
```

## Performance Tuning

### Multi-Threading
FFmpeg automatically uses multiple cores. Override if needed:

```bash
# Limit threads
ffmpeg -threads 4 -i input.mp4 -c:v libx264 output.mp4

# Auto (default)
ffmpeg -threads 0 -i input.mp4 -c:v libx264 output.mp4
```

### Tune Options
Optimize encoder for specific content types:

```bash
# Film content
ffmpeg -i input.mp4 -c:v libx264 -tune film -crf 22 output.mp4

# Animation
ffmpeg -i input.mp4 -c:v libx264 -tune animation -crf 22 output.mp4

# Grain (film with noise)
ffmpeg -i input.mp4 -c:v libx264 -tune grain -crf 22 output.mp4

# Low latency streaming
ffmpeg -i input.mp4 -c:v libx264 -tune zerolatency -crf 22 output.mp4

# Screen content (sharp edges)
ffmpeg -i input.mp4 -c:v libx264 -tune stillimage -crf 22 output.mp4
```

## Advanced Encoding (Deep Cuts)

Lower-level controls for precise output. Use these when CRF and presets aren't enough — typically when target file size, broadcast spec, or codec-internal behavior matter.

### Two-Pass VBR (precise file size)
Two-pass variable bitrate hits a target average bitrate (and therefore file size) with quality distributed where it matters.

```bash
# Pass 1: analysis only, no output written
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null /dev/null

# Pass 2: actual encode using stats from pass 1
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac -b:a 128k output.mp4

# Custom passlogfile (avoid clobbering between parallel jobs)
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -passlogfile /tmp/job1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -passlogfile /tmp/job1 -c:a aac output.mp4

# With min/max bitrate constraints (capped VBR)
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -minrate 1M -maxrate 4M -bufsize 8M -c:a aac output.mp4
```

### CBR (Constant Bitrate)
Constant bitrate is required for broadcast and some live transports. Larger files than VBR for same quality.

```bash
# Strict CBR via min/max equal to target
ffmpeg -i input.mp4 -c:v libx264 \
  -b:v 4M -minrate 4M -maxrate 4M -bufsize 8M \
  -x264-params "nal-hrd=cbr" \
  -c:a aac -b:a 128k output.mp4

# CBR with H.265
ffmpeg -i input.mp4 -c:v libx265 \
  -b:v 3M -minrate 3M -maxrate 3M -bufsize 6M \
  -x265-params "vbv-bufsize=6000:vbv-maxrate=3000:vbv-minrate=3000" \
  output.mp4
```

### GOP / Keyframe Placement
Group-of-pictures size and keyframe positioning. Critical for seeking, segment alignment, and cut points.

```bash
# Fixed GOP size (keyframe every N frames)
ffmpeg -i input.mp4 -c:v libx264 -g 60 -keyint_min 60 -sc_threshold 0 output.mp4

# Force keyframe at scene cuts (default behavior)
ffmpeg -i input.mp4 -c:v libx264 -g 250 -keyint_min 25 output.mp4

# Force keyframes at specific timestamps
ffmpeg -i input.mp4 -c:v libx264 -force_key_frames "0,5,10,15,20" output.mp4

# Force keyframe every N seconds (expression form)
ffmpeg -i input.mp4 -c:v libx264 -force_key_frames "expr:gte(t,n_forced*2)" output.mp4

# Closed GOP (no inter-GOP references — required for some streaming spec)
ffmpeg -i input.mp4 -c:v libx264 -g 60 -keyint_min 60 -sc_threshold 0 -flags +cgop output.mp4
```

### Profiles & Levels
Codec profiles cap which features the encoder uses (B-frames, bit depth, chroma subsampling). Levels cap resolution/bitrate. Use for device compatibility.

```bash
# H.264 baseline (no B-frames, max compatibility — old phones, embedded)
ffmpeg -i input.mp4 -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p output.mp4

# H.264 main (most consumer devices)
ffmpeg -i input.mp4 -c:v libx264 -profile:v main -level 4.0 -pix_fmt yuv420p output.mp4

# H.264 high (best quality, modern devices)
ffmpeg -i input.mp4 -c:v libx264 -profile:v high -level 4.2 -pix_fmt yuv420p output.mp4

# H.265 main (8-bit, standard)
ffmpeg -i input.mp4 -c:v libx265 -profile:v main -pix_fmt yuv420p output.mp4

# H.265 main10 (10-bit, HDR)
ffmpeg -i input.mp4 -c:v libx265 -profile:v main10 -pix_fmt yuv420p10le output.mp4
```

### x264 Advanced Options
Direct passthrough to x264. Use `-x264-params key=value:key=value` syntax. Overrides any flag-based equivalents.

```bash
# Reference frames + B-frames + adaptive B
ffmpeg -i input.mp4 -c:v libx264 \
  -x264-params "ref=4:bframes=3:b-adapt=2:b-pyramid=normal" \
  output.mp4

# CABAC entropy coding (default in main+ profiles)
ffmpeg -i input.mp4 -c:v libx264 \
  -x264-params "cabac=1:trellis=2:me=umh:subme=10" \
  output.mp4

# Film grain preservation
ffmpeg -i input.mp4 -c:v libx264 \
  -x264-params "aq-mode=3:aq-strength=1.0:psy-rd=1.0,0.15" \
  output.mp4

# Lossless H.264
ffmpeg -i input.mp4 -c:v libx264 -x264-params "qp=0" -preset veryslow output.mp4
```

### x265 Advanced Options
Direct passthrough to x265.

```bash
# Reference frames + B-frames + lookahead
ffmpeg -i input.mp4 -c:v libx265 \
  -x265-params "ref=4:bframes=4:rc-lookahead=40:b-adapt=2" \
  output.mp4

# Sample-adaptive offset (SAO) on
ffmpeg -i input.mp4 -c:v libx265 \
  -x265-params "sao=1:strong-intra-smoothing=1" \
  output.mp4

# Lossless H.265
ffmpeg -i input.mp4 -c:v libx265 -x265-params "lossless=1" output.mp4

# Suppress x265 stats banner
ffmpeg -i input.mp4 -c:v libx265 -x265-params "log-level=error" output.mp4
```

### Interactions & Overrides

Common collisions between deep-cut flags. Track these when combining options:

| Combo | What happens |
|---|---|
| `-tune zerolatency` + `-bf 3` | Tune zerolatency forces `bframes=0` — your `-bf 3` is silently ignored. |
| `-profile:v baseline` + B-frames | Baseline forbids B-frames — encoder drops B-frames automatically. |
| `-x264-params "bframes=3"` + flag `-bf 5` | `-x264-params` wins. The flag is ignored without warning. |
| `-crf 22` + `-b:v 2M` | CRF wins; bitrate target ignored unless you switch to two-pass. |
| Two-pass + `-crf` | Two-pass requires `-b:v`; CRF is ignored. |
| `-pix_fmt yuv422p` + `-profile:v baseline` | Baseline requires yuv420p — encode fails. Match `pix_fmt` to profile. |
| Closed GOP (`-flags +cgop`) + scene-cut keyframes | `-sc_threshold 0` is required — otherwise scene cuts insert open-GOP keyframes. |

Rule of thumb: if a flag and an `-x*-params` setting touch the same knob, the params string wins. Specify each setting in only one place.

## Codec Selection Guide

### Use Cases

| Use Case | Codec | Settings |
|----------|-------|----------|
| Web video | H.264 | CRF 23, preset medium |
| 4K streaming | H.265 | CRF 24, preset fast |
| YouTube upload | VP9 or H.264 | CRF 23 |
| Archive | H.265 or H.264 | CRF 18, preset slow |
| Low bandwidth | AV1 or H.265 | CRF 30 |
| Fast encoding | H.264 NVENC | preset fast |
| Maximum compatibility | H.264 | profile main, level 4.0 |

### Platform Compatibility

| Platform | Recommended | Supported |
|----------|------------|-----------|
| Web browsers | H.264 | H.264, VP9, AV1 |
| Mobile devices | H.264 | H.264, H.265 |
| Smart TVs | H.264 | H.264, H.265 |
| YouTube | VP9, H.264 | All |
| Social media | H.264 | H.264 |

## Best Practices

1. **Use CRF for most tasks** - Better than bitrate for variable content
2. **Start with CRF 23** - Good balance, adjust based on results
3. **Use slow preset** - For archival and final delivery
4. **Use fast preset** - For previews and testing
5. **Hardware acceleration** - When speed is critical
6. **Two-pass encoding** - When file size is fixed
7. **Match source frame rate** - Don't increase FPS
8. **Don't upscale resolution** - Keep original or downscale
9. **Test on short clips** - Verify settings before full encode
10. **Keep source files** - Original quality for re-encoding

## Troubleshooting

### Poor Quality Output
```bash
# Lower CRF value
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4

# Use slower preset
ffmpeg -i input.mp4 -c:v libx264 -crf 22 -preset veryslow output.mp4

# Increase bitrate (two-pass)
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 5M -pass 1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M -pass 2 -c:a aac output.mp4
```

### Slow Encoding
```bash
# Use faster preset
ffmpeg -i input.mp4 -c:v libx264 -preset ultrafast output.mp4

# Use hardware acceleration
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4

# Reduce resolution
ffmpeg -i input.mp4 -vf scale=1280:-1 -c:v libx264 output.mp4
```

### Large File Size
```bash
# Increase CRF
ffmpeg -i input.mp4 -c:v libx264 -crf 26 output.mp4

# Use better codec
ffmpeg -i input.mp4 -c:v libx265 -crf 26 output.mp4

# Two-pass with target bitrate
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 1M -pass 1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 2 -c:a aac output.mp4
```
