# FFmpeg Audio Effects

Detect silence, normalize loudness, apply effects (reverb / chorus / flanger / phaser), crossfade between tracks, concatenate, and split audio.

> **SoX is often better for audio.** ffmpeg's `aecho`, `chorus`, `flanger` are functional but primitive. SoX (`brew install sox`) ships proper algorithms (Schroeder reverb, multi-tap chorus). Recipes below note when SoX is the better tool. Both are valid; pick by quality target.

## Silence

Detect, remove, or insert silence.

```bash
# Detect silence (output to stderr — pipe to grep to capture timestamps)
ffmpeg -i input.mp3 -af "silencedetect=noise=-30dB:d=0.5" -f null - 2>&1 | grep silence

# Remove silence at start and end
ffmpeg -i input.mp3 -af "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-30dB:stop_periods=1:stop_silence=0.1:stop_threshold=-30dB" output.mp3

# Trim only leading silence
ffmpeg -i input.mp3 -af "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-30dB" output.mp3

# Insert 2 seconds of silence at start (apad)
ffmpeg -i input.mp3 -af "adelay=2000|2000" output.mp3

# Pad with silence to total duration
ffmpeg -i input.mp3 -af "apad=whole_dur=60" output.mp3
```

## Loudness Normalization (EBU R128)

Two-pass `loudnorm` is the broadcast standard. One-pass is faster but less precise.

### One-Pass Loudnorm

```bash
# Standard broadcast target (-23 LUFS, -1 dBTP true peak, 7 LU range)
ffmpeg -i input.mp3 -af "loudnorm=I=-23:TP=-1:LRA=7" output.mp3

# Streaming target (-16 LUFS — Spotify, Apple Podcasts)
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1:LRA=11" output.mp3

# YouTube target (-14 LUFS)
ffmpeg -i input.mp3 -af "loudnorm=I=-14:TP=-1:LRA=11" output.mp3
```

### Two-Pass Loudnorm (Preferred)

```bash
# Pass 1: measure (output captured for pass 2)
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | tail -n 12

# Copy the measured_I, measured_TP, measured_LRA, measured_thresh, target_offset values

# Pass 2: apply with measured values
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1:LRA=11:measured_I=-22.4:measured_TP=-2.3:measured_LRA=4.5:measured_thresh=-32.4:offset=0.7:linear=true" output.mp3
```

### Dynamic Audio Normalization (alternative)

`dynaudnorm` is per-frame normalization — different goal than loudnorm. Use for bringing up quiet parts in podcasts/voice.

```bash
# Default settings
ffmpeg -i input.mp3 -af "dynaudnorm" output.mp3

# More aggressive (smaller window, stronger gain)
ffmpeg -i input.mp3 -af "dynaudnorm=f=200:g=15" output.mp3
```

## Reverb

ffmpeg's `aecho` is single-tap echo, not real reverb.

```bash
# Single-tap echo (ffmpeg native)
ffmpeg -i input.mp3 -af "aecho=0.8:0.9:1000:0.3" output.mp3

# Multi-tap echo (chained)
ffmpeg -i input.mp3 -af "aecho=0.8:0.9:1000|2000|3000:0.3|0.2|0.1" output.mp3
```

> **SoX is better.** For real reverb (room/hall/plate simulation):
> ```bash
> sox input.mp3 output.mp3 reverb 50 50 100
> # reverb <reverberance> <hf-damping> <room-scale>
> ```
> ffmpeg `afir` (convolution with impulse-response file) is closer to a real reverb but requires you supply an IR `.wav` file.

## Chorus

```bash
# ffmpeg chorus (basic)
ffmpeg -i input.mp3 -af "chorus=0.7:0.9:55:0.4:0.25:2" output.mp3
```

> **SoX equivalent (better quality):**
> ```bash
> sox input.mp3 output.mp3 chorus 0.7 0.9 55 0.4 0.25 2 -t
> ```

## Flanger

```bash
ffmpeg -i input.mp3 -af "flanger=delay=10:depth=2:regen=10" output.mp3
```

> **SoX equivalent:**
> ```bash
> sox input.mp3 output.mp3 flanger 10 2 0 71 0.5 sine 25 linear
> ```

## Phaser

```bash
ffmpeg -i input.mp3 -af "aphaser=in_gain=0.4:out_gain=0.74:delay=3:decay=0.4:speed=0.5" output.mp3
```

## Distortion / Crusher

```bash
# Bit crusher (lo-fi sample-rate / bit-depth reduction)
ffmpeg -i input.mp3 -af "acrusher=bits=8:mode=log:samples=2" output.mp3

# Aggressive crush
ffmpeg -i input.mp3 -af "acrusher=bits=4:mode=lin:samples=8" output.mp3
```

## Audio Crossfade

Smooth transition between two tracks.

```bash
# Crossfade two tracks over 5 seconds
ffmpeg -i track1.mp3 -i track2.mp3 \
  -filter_complex "[0:a][1:a]acrossfade=d=5[a]" \
  -map "[a]" output.mp3

# Crossfade with fade-out curve choice
ffmpeg -i track1.mp3 -i track2.mp3 \
  -filter_complex "[0:a][1:a]acrossfade=d=3:c1=tri:c2=tri[a]" \
  -map "[a]" output.mp3
```

Curves: `tri` (triangular, default), `qsin` (quarter sine), `hsin` (half sine), `esin` (exponential sine), `log`, `ipar`, `qua`, `cub`, `squ`, `cbr`, `par`, `exp`, `iqsin`, `ihsin`, `dese`, `desi`, `losi`, `sinc`.

## Audio Concat & Split

### Concat (Same Codec)

```bash
# Demuxer concat (no re-encode — files must have same codec/sample rate/channels)
cat > list.txt <<EOF
file 'track1.mp3'
file 'track2.mp3'
file 'track3.mp3'
EOF
ffmpeg -f concat -safe 0 -i list.txt -c copy combined.mp3
```

### Concat (Mixed Codecs)

```bash
# Filter concat (re-encodes, accepts any inputs)
ffmpeg -i track1.mp3 -i track2.wav -i track3.flac \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]" \
  -map "[a]" combined.mp3
```

### Split

```bash
# Extract specific time range (no re-encode where possible)
ffmpeg -ss 00:01:30 -to 00:03:00 -i input.mp3 -c copy clip.mp3

# Re-encode for precise cut points
ffmpeg -i input.mp3 -ss 00:01:30 -to 00:03:00 -c:a libmp3lame -q:a 2 clip.mp3

# Split into N-second segments
ffmpeg -i input.mp3 -f segment -segment_time 60 -c copy seg_%03d.mp3
```

## Volume & Mixing

```bash
# Set absolute volume (multiplier)
ffmpeg -i input.mp3 -af "volume=0.5" output.mp3

# Volume in dB
ffmpeg -i input.mp3 -af "volume=-6dB" output.mp3

# Mix two tracks (sum with normalization)
ffmpeg -i track1.mp3 -i track2.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest[a]" \
  -map "[a]" output.mp3

# Mix with weights (track1 louder)
ffmpeg -i music.mp3 -i voice.mp3 \
  -filter_complex "[0:a]volume=0.3[bg];[1:v][bg]amix=inputs=2:duration=first[a]" \
  -map "[a]" output.mp3

# Stereo to mono
ffmpeg -i stereo.mp3 -af "pan=mono|c0=0.5*c0+0.5*c1" mono.mp3
```

## Common Recipes

### Master A Podcast Episode

```bash
# Two-pass loudnorm to -16 LUFS, then export to MP3 192k
ffmpeg -i raw.wav -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | tail -n 12
# (read measured values from output)
ffmpeg -i raw.wav -af "loudnorm=I=-16:TP=-1:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<th>:offset=<o>:linear=true" -c:a libmp3lame -b:a 192k podcast.mp3
```

### Trim Silence + Normalize Voice Recording

```bash
ffmpeg -i raw.wav -af "silenceremove=start_periods=1:start_silence=0.2:start_threshold=-40dB:stop_periods=1:stop_silence=0.2:stop_threshold=-40dB,dynaudnorm=f=300:g=15" cleaned.wav
```

### Add Background Music To Voiceover

```bash
ffmpeg -i voice.wav -i music.mp3 \
  -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first[a]" \
  -map "[a]" -c:a libmp3lame -b:a 192k mixed.mp3
```

### Strip Audio From Video And Master

```bash
ffmpeg -i video.mp4 -vn -af "loudnorm=I=-16:TP=-1:LRA=11" -c:a libmp3lame -b:a 192k extracted.mp3
```
