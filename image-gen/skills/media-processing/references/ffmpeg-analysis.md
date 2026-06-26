# FFmpeg Analysis

Inspect, measure, and detect content in videos. Scene-cut detection, histograms, motion estimation, blackout / freeze-frame detection, per-frame statistics, and ffprobe deep usage.

## Scene Detection

Detect cuts and produce timestamps or extract keyframes per scene.

```bash
# Print scene-change timestamps to stderr
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',showinfo" -f null - 2>&1 | grep -E 'pts_time'

# Extract one frame per scene change to JPEG
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',scale=320:-1" -vsync vfr scene_%03d.jpg

# Tighter threshold (catches subtle cuts)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.2)'" -vsync vfr scene_%03d.png

# Looser threshold (only major cuts)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.6)'" -vsync vfr scene_%03d.png

# Output scene timestamps as CSV
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',metadata=print:file=-" -an -f null - 2>&1 | grep "pts_time" | awk -F'pts_time:' '{print $2}'
```

Threshold meaning: 0.0–1.0 difference between consecutive frames. 0.4 is a balanced default for cuts; 0.2 catches dissolves; 0.6 catches only hard cuts.

## Histogram

Visualize tonal distribution.

```bash
# Generate histogram overlay video (256-bucket histogram drawn on each frame)
ffmpeg -i input.mp4 -vf "histogram" output.mp4

# Histogram on side, video on left
ffmpeg -i input.mp4 -vf "split[a][b];[b]histogram[h];[a][h]hstack" output.mp4

# Single-frame histogram as image
ffmpeg -ss 5 -i input.mp4 -vf "histogram" -vframes 1 hist.png

# Levels (separate R/G/B histograms vertically)
ffmpeg -i input.mp4 -vf "histogram=display_mode=parade" output.mp4
```

## Signalstats / Per-Frame Stats

Per-frame YUV / luminance statistics.

```bash
# Full signalstats (Y/U/V min/max/avg, sat, hue, etc. — output to log)
ffmpeg -i input.mp4 -vf "signalstats,metadata=print:file=stats.log" -f null -

# Show YAVG (average luminance) only
ffmpeg -i input.mp4 -vf "signalstats,metadata=print:file=-:key=lavfi.signalstats.YAVG" -f null - 2>&1

# Detect overexposure (any frame with YMAX = 255)
ffmpeg -i input.mp4 -vf "signalstats,metadata=print:file=-:key=lavfi.signalstats.YMAX" -f null - 2>&1 | grep "value=255"

# Per-frame metadata as JSON
ffmpeg -i input.mp4 -vf "signalstats,metadata=print:file=stats.json:format=json" -f null -
```

## Motion Estimation

Detect motion intensity per frame or section.

```bash
# Motion vectors visualization
ffmpeg -flags2 +export_mvs -i input.mp4 -vf codecview=mv=pf+bf+bb output.mp4

# Output motion-magnitude per frame (mestimate)
ffmpeg -i input.mp4 -vf "mestimate=method=epzs,metadata=print:file=motion.log" -f null -

# Detect static / low-motion segments (good for selecting interesting clips)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.05)',signalstats,metadata=print:file=-:key=lavfi.signalstats.YDIF" -f null - 2>&1
```

## Blackdetect / Freezedetect

Find black frames or frozen segments — useful for QC and ad-break detection.

```bash
# Detect black periods (≥2 seconds of black, threshold pixel <0.10, duration default)
ffmpeg -i input.mp4 -vf "blackdetect=d=2:pix_th=0.10" -an -f null - 2>&1 | grep blackdetect

# Detect frozen frames (≥2 seconds, similarity threshold)
ffmpeg -i input.mp4 -vf "freezedetect=n=0.001:d=2" -an -f null - 2>&1 | grep freezedetect

# Combined QC pass — black + freeze + signalstats
ffmpeg -i input.mp4 -vf "blackdetect,freezedetect=n=0.001:d=2,signalstats,metadata=print:file=qc.log" -an -f null -
```

## ffprobe Deep Usage

```bash
# Frame-level packet info (size, type, timestamp)
ffprobe -v error -show_frames -of json input.mp4 | head -100

# Keyframe positions
ffprobe -v error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=p=0 input.mp4 | grep K

# Bitrate per N seconds (rolling average via packet sizes)
ffprobe -v error -select_streams v:0 -show_entries packet=size,duration_time -of csv=p=0 input.mp4

# Codec-specific extradata
ffprobe -v error -show_streams -of json input.mp4 | jq '.streams[] | {codec: .codec_name, profile: .profile, level: .level}'

# Pixel format and color tags
ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt,color_space,color_primaries,color_transfer,color_range -of default=noprint_wrappers=1 input.mp4

# Get duration in seconds (cleanly)
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
```

## Frame-Level MD5 / Hash

Verify byte-level content integrity.

```bash
# Per-frame MD5 hashes
ffmpeg -i input.mp4 -f framemd5 -an frames.md5

# Compare two files frame-by-frame
ffmpeg -i a.mp4 -f framemd5 -an a.md5
ffmpeg -i b.mp4 -f framemd5 -an b.md5
diff a.md5 b.md5

# Single MD5 for entire video (decoded frames)
ffmpeg -i input.mp4 -f md5 -an -
```

## PSNR / SSIM (Quality Comparison)

Compare encoded output against the source.

```bash
# PSNR between original and encoded
ffmpeg -i original.mp4 -i encoded.mp4 -lavfi psnr -f null -

# SSIM (perceptual quality)
ffmpeg -i original.mp4 -i encoded.mp4 -lavfi ssim -f null -

# VMAF (Netflix perceptual metric — requires libvmaf build)
ffmpeg -i encoded.mp4 -i original.mp4 -lavfi libvmaf -f null -

# Both PSNR and SSIM, log to file
ffmpeg -i original.mp4 -i encoded.mp4 \
  -lavfi "[0:v][1:v]psnr=psnr.log;[0:v][1:v]ssim=ssim.log" \
  -f null -
```

## Audio Analysis

```bash
# Audio levels (peak, RMS) per frame
ffmpeg -i input.mp3 -af "astats=metadata=1,ametadata=print:file=audio.log" -f null -

# Loudness measurement (one-pass, EBU R128)
ffmpeg -i input.mp3 -af "ebur128" -f null - 2>&1 | tail -n 12

# Spectrum visualization
ffmpeg -i input.mp3 -lavfi showspectrum=size=1280x720 -f mp4 spectrum.mp4

# Audio waveform image
ffmpeg -i input.mp3 -filter_complex "showwavespic=s=1280x240" -frames:v 1 wave.png
```

## Common Recipes

### QC Pass On A Master File

```bash
# Black + freeze + signalstats + audio levels — single pass
ffmpeg -i master.mp4 -vf "blackdetect=d=2,freezedetect=n=0.001:d=2,signalstats,metadata=print:file=video_qc.log" -af "astats=metadata=1,ametadata=print:file=audio_qc.log,ebur128=peak=true" -f null - 2>&1 | tail -n 50
```

### Generate Scene-Based Contact Sheet

```bash
# Extract one frame per scene and tile into 5x5 grid
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',scale=320:180,tile=5x5" -frames:v 1 scenes.png
```

### Frame-Accurate Hash Verification (Two Encodes Identical?)

```bash
ffmpeg -i a.mp4 -f md5 -an - 
ffmpeg -i b.mp4 -f md5 -an - 
# If both MD5s match, the decoded video is byte-identical
```

### Detect Where Action Happens (High Motion)

```bash
ffmpeg -i input.mp4 -vf "select='gt(scene,0.05)',scale=320:180" -vsync vfr motion_%03d.jpg
```

### Inspect Bitrate Over Time

```bash
# Print packet sizes — pipe through awk for per-second bitrate
ffprobe -v error -select_streams v:0 -show_entries packet=size,pts_time -of csv=p=0 input.mp4 | \
  awk -F, 'BEGIN{prev=0;sum=0}{sec=int($1);if(sec>prev){print prev","sum*8/1000"kbps";sum=0;prev=sec}sum+=$2}'
```
