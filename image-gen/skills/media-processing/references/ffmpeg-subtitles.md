# FFmpeg Subtitles

Add, extract, convert, and style subtitles. Covers burn-in (hard-sub baked into video), soft-mux (selectable subtitle track in container), format conversion between SRT/ASS/VTT, and timing adjustments.

> **Requires libass** for burn-in and ASS rendering. Verify: `ffmpeg -filters 2>/dev/null | grep -E 'subtitles|ass'`. Stock Homebrew ffmpeg ships with libass; minimal builds may not.

## Burn-In Subtitles

Permanently render subtitles into the video frame. Output cannot be turned off by the player.

### Basic Burn-In

```bash
# Burn SRT subtitles into video
ffmpeg -i video.mp4 -vf "subtitles=subs.srt" -c:a copy output.mp4

# Burn ASS subtitles (advanced styling preserved)
ffmpeg -i video.mp4 -vf "ass=subs.ass" -c:a copy output.mp4

# Burn-in with re-encoded video (required — burning always re-encodes)
ffmpeg -i video.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 22 -c:a copy output.mp4
```

### Burn-In With Style Override

The `force_style` parameter applies inline styling to SRT (which has no native styling).

```bash
# Override font, size, color
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='Fontname=Helvetica,Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'" output.mp4

# Reposition (alignment 1-9, where 2 is bottom-center)
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='Alignment=2,MarginV=40'" output.mp4

# Background box behind text
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='BorderStyle=3,BackColour=&H80000000,Outline=0,Shadow=0'" output.mp4
```

### Burn-In From Container Stream

When subtitles are embedded in the source file as a track.

```bash
# Burn-in subtitle stream 0 from same file
ffmpeg -i video.mkv -vf "subtitles=video.mkv:si=0" -c:a copy output.mp4

# Pick a specific subtitle track by index
ffmpeg -i video.mkv -vf "subtitles=video.mkv:si=2" -c:a copy output.mp4

# Specify font directory (Linux fontconfig issues)
ffmpeg -i video.mkv -vf "subtitles=subs.ass:fontsdir=/usr/share/fonts" -c:a copy output.mp4
```

## Soft-Mux Subtitles

Embed subtitles as a selectable track in the container. Player can toggle on/off.

```bash
# Mux SRT into MKV (preserves original)
ffmpeg -i video.mp4 -i subs.srt -c copy -c:s srt output.mkv

# Mux into MP4 (must convert to mov_text)
ffmpeg -i video.mp4 -i subs.srt -c copy -c:s mov_text output.mp4

# Mux multiple subtitle tracks with language tags
ffmpeg -i video.mp4 -i en.srt -i es.srt \
  -map 0 -map 1 -map 2 -c copy -c:s mov_text \
  -metadata:s:s:0 language=eng -metadata:s:s:1 language=spa \
  output.mp4

# Set default subtitle track
ffmpeg -i video.mp4 -i subs.srt -c copy -c:s mov_text \
  -disposition:s:0 default \
  output.mp4
```

## Extract Subtitles

Pull subtitle tracks out of a container as standalone files.

```bash
# Extract first subtitle stream as SRT
ffmpeg -i video.mkv -map 0:s:0 -c:s srt subs.srt

# Extract as ASS (preserves styling if source is ASS)
ffmpeg -i video.mkv -map 0:s:0 -c:s ass subs.ass

# Extract as WebVTT
ffmpeg -i video.mkv -map 0:s:0 -c:s webvtt subs.vtt

# Extract all subtitle tracks at once
ffmpeg -i video.mkv -map 0:s -c:s srt sub_%d.srt

# List subtitle streams without extracting
ffprobe -loglevel error -select_streams s -show_entries stream=index,codec_name:stream_tags=language,title -of csv=p=0 video.mkv
```

## Format Conversion

Convert between subtitle formats.

```bash
# SRT to ASS (gain styling capability)
ffmpeg -i subs.srt subs.ass

# ASS to SRT (loses styling — only text + timing)
ffmpeg -i subs.ass subs.srt

# SRT to WebVTT (browser-native)
ffmpeg -i subs.srt subs.vtt

# WebVTT to SRT
ffmpeg -i subs.vtt subs.srt

# SubRip with explicit charset (fix garbled non-Latin text)
ffmpeg -sub_charenc CP1252 -i subs.srt -c:s utf8 subs_utf8.srt
```

## Timing & Sync

Adjust subtitle timing without re-typing them.

```bash
# Shift all subtitles forward by 2.5 seconds
ffmpeg -itsoffset 2.5 -i subs.srt -c copy shifted.srt

# Shift backward by 1 second
ffmpeg -itsoffset -1 -i subs.srt -c copy shifted.srt

# Stretch / compress timing (re-encode to apply)
ffmpeg -i subs.ass -filter:s "setpts=1.04*PTS" stretched.ass

# Shift subtitles when burning in (delay relative to video)
ffmpeg -i video.mp4 -itsoffset 2.5 -i subs.srt \
  -filter_complex "[0:v]subtitles=subs.srt[v]" \
  -map "[v]" -map 0:a -c:a copy output.mp4
```

## ASS / SSA Styling

Advanced SubStation Alpha format supports rich styling, positioning, and effects.

```bash
# Convert SRT to ASS, then edit the ASS for styling, then burn in
ffmpeg -i subs.srt subs.ass
# (edit subs.ass to set [V4+ Styles] block — Fontname, Fontsize, colors, etc.)
ffmpeg -i video.mp4 -vf "ass=subs.ass" -c:a copy output.mp4

# Apply font directory for ASS with custom fonts
ffmpeg -i video.mp4 -vf "ass=subs.ass:fontsdir=./my-fonts" -c:a copy output.mp4

# Force specific charset for ASS source
ffmpeg -i video.mp4 -vf "ass=subs.ass:charenc=UTF-8" -c:a copy output.mp4
```

## Common Recipes

### Add Translated Subs To Social Clip
```bash
# 1. Translate subs.srt externally (or write fresh)
# 2. Burn in with consistent style + bottom-center placement
ffmpeg -i clip.mp4 -vf "subtitles=translated.srt:force_style='Fontname=Helvetica Bold,Fontsize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=60'" -c:v libx264 -crf 20 -c:a copy social.mp4
```

### Soft-Sub Master File With Multi-Language
```bash
ffmpeg -i master.mp4 -i en.srt -i es.srt -i fr.srt \
  -map 0 -map 1 -map 2 -map 3 \
  -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=eng -metadata:s:s:0 title=English \
  -metadata:s:s:1 language=spa -metadata:s:s:1 title=Español \
  -metadata:s:s:2 language=fra -metadata:s:s:2 title=Français \
  master_subbed.mp4
```

### Strip All Subtitles
```bash
# Remove all subtitle tracks, keep video + audio
ffmpeg -i video.mkv -map 0 -map -0:s -c copy clean.mkv
```

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Unable to load font` / `fontconfig: no font` | Linux can't find fonts | Add `:fontsdir=/path/to/fonts` to filter, or `force_style='Fontname=DejaVu Sans'` (a font fontconfig has) |
| Garbled / mojibake non-ASCII | Wrong charset | Add `:charenc=UTF-8` to filter, or pre-convert with `-sub_charenc <encoding>` |
| `Could not find tag for codec subrip in stream #0` | Wrong container codec | MP4 needs `-c:s mov_text`; MKV uses `-c:s srt` |
| Burn-in succeeds but no subtitles visible | Subtitles outside video frame timing | Check timestamps with `ffprobe subs.srt`; shift with `-itsoffset` |
| Filter fails on Windows path | Backslashes parsed as escapes | Use forward slashes or escape: `subtitles='C\:/path/subs.srt'` |
