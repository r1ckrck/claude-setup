# FFmpeg Composition

Combine multiple videos and images: stack into grids, picture-in-picture, chromakey/greenscreen, transitions between clips, concatenation, slideshows, and montages.

## Stacking

Place multiple videos side by side or top/bottom.

### Horizontal Stack (hstack)

```bash
# Two videos side by side
ffmpeg -i left.mp4 -i right.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Three videos in a row
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 \
  -filter_complex "[0:v][1:v][2:v]hstack=inputs=3[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Pre-scale each input to match (avoid hstack failure on size mismatch)
ffmpeg -i a.mp4 -i b.mp4 \
  -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[a][b]hstack[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

### Vertical Stack (vstack)

```bash
# Two videos stacked top/bottom
ffmpeg -i top.mp4 -i bottom.mp4 \
  -filter_complex "[0:v][1:v]vstack=inputs=2[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Three vertical (good for 9:16 social aggregation)
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 \
  -filter_complex "[0:v][1:v][2:v]vstack=inputs=3[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

### Grid (xstack)

For 2x2, 3x3, or arbitrary grid layouts.

```bash
# 2x2 grid (4 videos)
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -i d.mp4 \
  -filter_complex "[0:v][1:v][2:v][3:v]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]" \
  -map "[v]" -c:v libx264 output.mp4

# 3x3 grid (9 videos)
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -i d.mp4 -i e.mp4 -i f.mp4 -i g.mp4 -i h.mp4 -i i.mp4 \
  -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v]xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h3|w0_h0+h3|w0+w1_h0+h3[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

## Picture-in-Picture

Overlay one video inside another.

```bash
# PiP top-right corner with 320x180 inset
ffmpeg -i main.mp4 -i pip.mp4 \
  -filter_complex "[1:v]scale=320:180[pip];[0:v][pip]overlay=W-w-10:10[v]" \
  -map "[v]" -map 0:a -c:v libx264 -c:a copy output.mp4

# PiP bottom-left corner
ffmpeg -i main.mp4 -i pip.mp4 \
  -filter_complex "[1:v]scale=320:180[pip];[0:v][pip]overlay=10:H-h-10[v]" \
  -map "[v]" -map 0:a -c:v libx264 output.mp4

# PiP with rounded corner mask (use alpha)
ffmpeg -i main.mp4 -i pip.mp4 \
  -filter_complex "[1:v]scale=320:180,format=yuva420p,geq=lum='lum(X,Y)':a='if(lt(pow(X-(W/2),2)+pow(Y-(H/2),2)\\,pow(W/2,2))\\,255\\,0)'[pip];[0:v][pip]overlay=W-w-10:10[v]" \
  -map "[v]" -c:v libx264 output.mp4

# PiP with border
ffmpeg -i main.mp4 -i pip.mp4 \
  -filter_complex "[1:v]scale=320:180,pad=iw+8:ih+8:4:4:white[pip];[0:v][pip]overlay=W-w-10:10[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

## Chromakey / Greenscreen

Remove a solid color background to create transparency for compositing.

```bash
# Remove green screen (default green)
ffmpeg -i greenscreen.mp4 -i background.mp4 \
  -filter_complex "[0:v]chromakey=0x00FF00:0.1:0.0[ckout];[1:v][ckout]overlay[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Remove blue screen
ffmpeg -i bluescreen.mp4 -i background.mp4 \
  -filter_complex "[0:v]chromakey=0x0000FF:0.15:0.0[ckout];[1:v][ckout]overlay[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Tighter key (similarity 0.05) with edge blending (blend 0.1)
ffmpeg -i fg.mp4 -i bg.mp4 \
  -filter_complex "[0:v]chromakey=0x00FF00:0.05:0.1[ckout];[1:v][ckout]overlay[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Color key (alpha cutoff for any color, no blending — sharp edges)
ffmpeg -i fg.mp4 -i bg.mp4 \
  -filter_complex "[0:v]colorkey=0x00FF00:0.3:0.2[ckout];[1:v][ckout]overlay[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

`chromakey` does YUV-based blending (smoother edges); `colorkey` does RGB-based hard cutoff (sharper edges, faster).

## Transitions (xfade)

Crossfade between two clips with a chosen transition.

```bash
# Simple fade transition (1-second crossfade at 5s mark)
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=5[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Wipe right
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=wiperight:duration=1:offset=5[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Slide up
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=slideup:duration=1:offset=5[v]" \
  -map "[v]" -c:v libx264 output.mp4

# Circle open
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=circleopen:duration=1.5:offset=5[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

### Transition Types

| Category | Transitions |
|---|---|
| Fades | `fade`, `fadeblack`, `fadewhite`, `fadegrays` |
| Wipes | `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `wipetl`, `wipetr`, `wipebl`, `wipebr` |
| Slides | `slideleft`, `slideright`, `slideup`, `slidedown` |
| Smooth slides | `smoothleft`, `smoothright`, `smoothup`, `smoothdown` |
| Reveals | `circlecrop`, `rectcrop`, `circleopen`, `circleclose`, `vertopen`, `vertclose`, `horzopen`, `horzclose`, `diagtl`, `diagtr`, `diagbl`, `diagbr` |
| Effects | `dissolve`, `pixelize`, `radial`, `hblur`, `hlslice`, `vlslice`, `vuslice`, `hrslice`, `vrslice`, `distance`, `squeezeh`, `squeezev`, `zoomin` |

## Concatenation

Two paths: demuxer (no re-encode, fast) vs filter (re-encodes, accepts mismatched inputs).

| Use | Path | Speed | Codec match required? |
|---|---|---|---|
| Same codec, container, params | demuxer | Instant (stream copy) | Yes — fails silently on mismatch |
| Mixed codecs / sizes / framerates | filter | Slow (re-encode) | No |

### Concat Demuxer (fast, no re-encode)

```bash
# 1. Create list file (one per line, file '<path>')
cat > list.txt <<EOF
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
EOF

# 2. Concat with stream copy
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Single-line generation of list.txt (sorted)
for f in *.mp4; do echo "file '$f'"; done > list.txt

# Concat with re-mux only (no re-encode but rebuild container)
ffmpeg -f concat -safe 0 -i list.txt -movflags +faststart -c copy output.mp4
```

### Concat Filter (re-encodes, mixes inputs)

```bash
# Concat two clips (one video stream + one audio stream each)
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 output.mp4

# Three clips with different sizes (pre-scale to match)
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex "[0:v]scale=1920:1080[v0];[1:v]scale=1920:1080[v1];[2:v]scale=1920:1080[v2];[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 output.mp4

# Video-only concat (no audio)
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 output.mp4
```

## Slideshow From Image Sequence

Build a video from numbered images.

```bash
# Each image displayed for 2 seconds (15 fps means 30 frames per image)
ffmpeg -framerate 1/2 -i img%03d.jpg -c:v libx264 -r 30 -pix_fmt yuv420p slideshow.mp4

# With background music
ffmpeg -framerate 1/3 -i img%03d.jpg -i music.mp3 -c:v libx264 -c:a aac -shortest slideshow.mp4

# Each image with crossfade transition (use xfade in a chain)
ffmpeg -loop 1 -t 3 -i img1.jpg -loop 1 -t 3 -i img2.jpg -loop 1 -t 3 -i img3.jpg \
  -filter_complex "[0:v][1:v]xfade=fade:1:2[v01];[v01][2:v]xfade=fade:1:5[v]" \
  -map "[v]" -c:v libx264 -pix_fmt yuv420p slideshow.mp4

# Sequence with arbitrary filenames (use glob)
ffmpeg -framerate 2 -pattern_type glob -i 'photos/*.jpg' -c:v libx264 -pix_fmt yuv420p slideshow.mp4
```

## Montage Tile

Tile multiple thumbnails into a single contact-sheet-style image (usually rendered with ImageMagick — see `imagemagick-batch.md` — but ffmpeg can do it for video frames).

```bash
# Extract 9 evenly-spaced thumbnails and tile in 3x3
ffmpeg -i video.mp4 -vf "select='not(mod(n\,250))',scale=320:180,tile=3x3" -frames:v 1 montage.png

# 5x5 contact sheet (every 100th frame)
ffmpeg -i video.mp4 -vf "select='not(mod(n\,100))',scale=160:90,tile=5x5" -frames:v 1 sheet.png
```

## Common Recipes

### Multi-Clip Slideshow With Crossfades + Audio Crossfade

```bash
# 3-clip slideshow with xfade transitions and acrossfade audio
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex \
    "[0:v][1:v]xfade=fade:1:5[v01]; \
     [v01][2:v]xfade=fade:1:11[v]; \
     [0:a][1:a]acrossfade=d=1[a01]; \
     [a01][2:a]acrossfade=d=1[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -c:a aac output.mp4
```

### Greenscreen Composite + Background Loop

```bash
ffmpeg -stream_loop -1 -i background.mp4 -i fg_greenscreen.mp4 \
  -filter_complex "[1:v]chromakey=0x00FF00:0.1:0.05[ckout];[0:v][ckout]overlay[v]" \
  -map "[v]" -map 1:a -shortest -c:v libx264 -c:a copy output.mp4
```

### Side-By-Side Comparison (Before/After)

```bash
ffmpeg -i before.mp4 -i after.mp4 \
  -filter_complex \
    "[0:v]scale=960:540,drawtext=text='BEFORE':x=10:y=10:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5[a]; \
     [1:v]scale=960:540,drawtext=text='AFTER':x=10:y=10:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5[b]; \
     [a][b]hstack[v]" \
  -map "[v]" -c:v libx264 compare.mp4
```
