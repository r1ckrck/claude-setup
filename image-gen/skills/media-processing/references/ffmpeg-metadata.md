# FFmpeg Metadata

Read, write, strip, and copy metadata across video, audio, and image files. ffmpeg handles container-level metadata (MP4 atoms, MKV tags, MP3 ID3) and stream tags. For image-specific metadata (EXIF, IPTC, XMP), use `exiftool` — recipes below cover both tools.

## Read Metadata

### ffprobe (Container & Stream)

```bash
# All metadata as JSON
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Format-level tags only
ffprobe -v quiet -print_format json -show_format input.mp4

# Specific stream tags (e.g., video stream)
ffprobe -v quiet -print_format json -show_streams -select_streams v:0 input.mp4

# Single field
ffprobe -v error -show_entries format_tags=title -of default=noprint_wrappers=1 input.mp4

# Duration in seconds
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

# Codec, resolution, framerate in CSV
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate \
  -of csv=p=0 input.mp4
```

### exiftool (EXIF / IPTC / XMP)

```bash
# All metadata
exiftool image.jpg

# Specific fields
exiftool -DateTimeOriginal -GPSPosition -Camera image.jpg

# JSON output
exiftool -j image.jpg

# CSV across multiple files
exiftool -csv -DateTimeOriginal -ImageWidth -ImageHeight *.jpg
```

## Write Metadata

### Container-Level Tags (ffmpeg)

```bash
# Set title, artist, year
ffmpeg -i input.mp4 -c copy \
  -metadata title="My Video" \
  -metadata artist="Studio X" \
  -metadata date="2026" \
  -metadata comment="Final master" \
  output.mp4

# Set per-stream tag (e.g., language on audio track)
ffmpeg -i input.mkv -c copy -metadata:s:a:0 language=eng output.mkv

# Set multiple tags including copyright
ffmpeg -i input.mp4 -c copy \
  -metadata title="Episode 1" \
  -metadata artist="Series Name" \
  -metadata album="Season 1" \
  -metadata track="1/10" \
  -metadata copyright="(c) 2026 Studio" \
  -metadata genre="Documentary" \
  output.mp4

# MKV-specific tags (more flexible than MP4)
ffmpeg -i input.mkv -c copy \
  -metadata DESCRIPTION="Long-form description" \
  -metadata ENCODER="ffmpeg 6.0" \
  output.mkv
```

### Audio Tags (ID3)

```bash
# MP3 ID3 tags
ffmpeg -i input.mp3 -c copy \
  -metadata title="Track Title" \
  -metadata artist="Artist Name" \
  -metadata album="Album Name" \
  -metadata track="3/12" \
  -metadata year="2026" \
  -metadata genre="Electronic" \
  output.mp3

# Embed cover art
ffmpeg -i input.mp3 -i cover.jpg -map 0 -map 1 \
  -c copy -id3v2_version 3 \
  -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" \
  output.mp3
```

### Image Metadata (exiftool)

```bash
# Write EXIF DateTime
exiftool -DateTimeOriginal="2026:04:25 14:30:00" image.jpg

# Write copyright + creator
exiftool -Copyright="(c) 2026 You" -Creator="Your Name" image.jpg

# Write IPTC
exiftool -IPTC:Caption-Abstract="Photo description" -IPTC:Keywords+="travel" -IPTC:Keywords+="2026" image.jpg

# Write XMP
exiftool -XMP:Title="Title" -XMP:Description="Long description" image.jpg
```

## Strip Metadata

Privacy-critical for shared assets. Removes camera info, GPS, timestamps.

### ffmpeg (Video / Audio)

```bash
# Strip all metadata, copy streams (fastest)
ffmpeg -i input.mp4 -map_metadata -1 -c copy clean.mp4

# Strip and force bit-exact output (no encoder watermark)
ffmpeg -i input.mp4 -map_metadata -1 -fflags +bitexact -c copy clean.mp4

# Strip from MP3 (keep audio data)
ffmpeg -i input.mp3 -map_metadata -1 -c:a copy clean.mp3

# Strip but preserve specific stream tag (e.g., language)
ffmpeg -i input.mkv -map_metadata -1 \
  -metadata:s:a:0 language=eng \
  -c copy clean.mkv
```

### exiftool (Images)

```bash
# Strip ALL metadata
exiftool -all= image.jpg

# Strip but preserve orientation (avoid 90° rotation on phone photos)
exiftool -all= -tagsfromfile @ -Orientation image.jpg

# Strip but preserve ICC profile (avoid wide-gamut color shift)
exiftool -all= -tagsfromfile @ -ICC_Profile image.jpg

# Strip but preserve both orientation AND ICC (recommended default)
exiftool -all= -tagsfromfile @ -Orientation -ICC_Profile image.jpg

# Strip GPS only
exiftool -gps:all= image.jpg

# Batch strip across folder (in-place — keep originals!)
exiftool -all= -tagsfromfile @ -Orientation -ICC_Profile -overwrite_original *.jpg
```

> **Footgun:** `exiftool -all=` strips orientation EXIF, which causes phone photos to display rotated 90° (the JPEG bytes are stored in landscape, the orientation tag tells the viewer to rotate). And it strips ICC, which makes wide-gamut images shift on color-managed displays. **Always preserve orientation and ICC by default.** Use the recipes above with `-tagsfromfile @`.

## Chapters

```bash
# Read chapter list
ffprobe -v quiet -print_format json -show_chapters input.mp4

# Write chapters from a metadata file
# 1. Create chapters.txt:
cat > chapters.txt <<EOF
;FFMETADATA1
title=My Video

[CHAPTER]
TIMEBASE=1/1000
START=0
END=60000
title=Intro

[CHAPTER]
TIMEBASE=1/1000
START=60000
END=180000
title=Part 1

[CHAPTER]
TIMEBASE=1/1000
START=180000
END=300000
title=Conclusion
EOF

# 2. Apply chapters
ffmpeg -i input.mp4 -i chapters.txt -map_metadata 1 -c copy chaptered.mp4

# Strip all chapters
ffmpeg -i input.mp4 -map_chapters -1 -c copy nochap.mp4
```

## GPS

### Read GPS From Image

```bash
# All GPS tags
exiftool -gps:all image.jpg

# Lat/Long only, decimal format
exiftool -GPSLatitude# -GPSLongitude# image.jpg

# Generate Google Maps URL
exiftool -if '$gpslatitude' -p 'https://maps.google.com/?q=$gpslatitude,$gpslongitude' image.jpg
```

### Write GPS

```bash
# Set lat/long (note: needs ref tags too — N/S/E/W)
exiftool -GPSLatitude=37.7749 -GPSLatitudeRef=N \
         -GPSLongitude=-122.4194 -GPSLongitudeRef=W \
         image.jpg

# Strip GPS only (privacy — common requirement before sharing)
exiftool -gps:all= image.jpg
```

### GPS On Video

```bash
# Read (MP4 with com.apple.quicktime.location.ISO6709 atom)
ffprobe -v quiet -print_format json -show_format input.mov | grep location

# Write GPS to MP4 (Apple location atom)
ffmpeg -i input.mp4 -c copy -metadata location="+37.7749-122.4194/" output.mp4
```

## Copy Metadata Between Files

```bash
# Copy all metadata from source to target
ffmpeg -i source.mp4 -i target.mp4 -map 1 -map_metadata 0 -c copy result.mp4

# Copy EXIF from one image to another
exiftool -tagsfromfile source.jpg -all:all target.jpg

# Copy specific tags only
exiftool -tagsfromfile source.jpg -DateTimeOriginal -Copyright target.jpg
```

## Common Recipes

### Privacy-Strip Phone Photo
```bash
# Remove GPS + camera serial + most EXIF, preserve orientation + ICC
exiftool -all= -tagsfromfile @ -Orientation -ICC_Profile -overwrite_original photo.jpg
```

### Tag MP4 As Master Copy
```bash
ffmpeg -i raw.mp4 -c copy \
  -metadata title="Project X — Master" \
  -metadata copyright="(c) 2026 Studio" \
  -metadata comment="Color-graded final, do not re-encode" \
  -metadata encoder="ffmpeg + DaVinci Resolve" \
  master.mp4
```

### Bulk Caption Photos With Date + Location
```bash
exiftool -DateTimeOriginal="2026:04:25 14:30:00" \
         -GPSLatitude=37.7749 -GPSLatitudeRef=N \
         -GPSLongitude=-122.4194 -GPSLongitudeRef=W \
         -IPTC:Keywords+="San Francisco" \
         -overwrite_original *.jpg
```

### Verify A File Has Been Stripped Clean
```bash
# ffprobe should show only essential codec info, no tags
ffprobe -v quiet -print_format json -show_format clean.mp4 | grep -A1 tags

# exiftool count of remaining tags
exiftool -a -G1 clean.jpg | wc -l
```
