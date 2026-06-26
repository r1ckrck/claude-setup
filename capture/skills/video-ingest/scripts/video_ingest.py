#!/usr/bin/env python3
"""video-ingest pipeline: download a video URL, transcribe audio, build frame contact sheets.

Subcommands (each prints one line of JSON to stdout; exits non-zero with {"error": ...} on failure):
  prepare --url <URL>      download + probe + transcribe + pass-1 contact sheet
  scenes  --workdir <dir>  pass-2 scene-change contact sheet (conditional)
  cleanup --workdir <dir>  remove the workdir (must be under TMPROOT)
"""

import argparse
import datetime
import json
import os
import re
import secrets
import shutil
import subprocess
import sys

YTDLP = "/opt/homebrew/bin/yt-dlp"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
WHISPERX = os.path.expanduser(os.environ.get("WHISPERX_BIN", "~/.local/bin/whisperx"))
INBOX = os.path.expanduser(os.environ.get("INGEST_INBOX", "~/inbox-remote"))
TMPROOT = os.path.expanduser(os.environ.get("INGEST_TMPROOT", "~/.cache/video-ingest"))

TARGET_FRAMES = 16
GRID = "4x4"
THUMB_W = 480
SCENE_THRESHOLD = 0.4
WARN_SECONDS = 1800

INSTAGRAM_RE = re.compile(r"https?://(www\.)?instagram\.com/", re.I)
YOUTUBE_RE = re.compile(r"https?://((www\.)?youtube\.com/|youtu\.be/)", re.I)


def die(msg, **extra):
    """Print a JSON error and exit non-zero — the stop-on-failure contract."""
    payload = {"error": msg}
    payload.update(extra)
    print(json.dumps(payload))
    sys.exit(1)


def emit(obj):
    print(json.dumps(obj))
    sys.exit(0)


def run(cmd, **kwargs):
    """Run a command, capturing output. Returns CompletedProcess; never raises."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def platform_of(url):
    if INSTAGRAM_RE.search(url):
        return "Instagram"
    if YOUTUBE_RE.search(url):
        return "YouTube"
    return None


def ffprobe_json(args):
    proc = run([FFPROBE, "-v", "error", *args, "-of", "json"])
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def source_fps(video):
    data = ffprobe_json(["-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", video])
    try:
        rate = data["streams"][0]["r_frame_rate"]
        num, den = rate.split("/")
        return float(num) / float(den) if float(den) else None
    except (TypeError, KeyError, IndexError, ValueError, ZeroDivisionError):
        return None


def cmd_prepare(args):
    url = args.url
    platform = platform_of(url)
    if not platform:
        die("unsupported platform", detail="URL is not instagram.com or youtube.com/youtu.be")

    slug = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    workdir = os.path.join(TMPROOT, f"{slug}-{secrets.token_hex(2)}")
    os.makedirs(workdir, exist_ok=True)

    def fail(msg, **extra):
        """Die, but first remove the workdir we just created — no orphan temp on failure."""
        if os.path.commonpath([os.path.abspath(workdir), TMPROOT]) == TMPROOT:
            shutil.rmtree(workdir, ignore_errors=True)
        die(msg, **extra)

    # 1. Download video + metadata
    dl = run([
        YTDLP, "-f", "bv*+ba/b", "--merge-output-format", "mp4",
        "-o", os.path.join(workdir, "video.%(ext)s"),
        "--write-info-json", "--no-playlist", "--retries", "3", url,
    ])
    if dl.returncode != 0:
        last = (dl.stderr.strip().splitlines() or ["unknown error"])[-1]
        fail("download failed", detail=last)

    video = os.path.join(workdir, "video.mp4")
    if not os.path.exists(video):
        # yt-dlp may have kept a non-mp4 container despite the merge hint
        candidates = [f for f in os.listdir(workdir) if f.startswith("video.") and not f.endswith(".info.json")]
        if not candidates:
            fail("download failed", detail="no video file produced")
        video = os.path.join(workdir, candidates[0])

    # 2. Parse metadata
    info = {}
    for f in os.listdir(workdir):
        if f.endswith(".info.json"):
            try:
                with open(os.path.join(workdir, f)) as fh:
                    info = json.load(fh)
            except (OSError, json.JSONDecodeError):
                info = {}
            break

    title = info.get("title") or info.get("fulltitle") or "(untitled)"
    uploader = info.get("uploader") or info.get("channel") or info.get("uploader_id") or "(unknown)"
    webpage_url = info.get("webpage_url") or url
    caption = info.get("description") or ""

    duration = info.get("duration")
    if not duration:
        dprobe = ffprobe_json(["-show_entries", "format=duration", video])
        try:
            duration = float(dprobe["format"]["duration"])
        except (TypeError, KeyError, ValueError):
            duration = 0.0
    duration = float(duration)

    result = {
        "slug": slug,
        "out_name": f"{slug}-video-ingest",
        "workdir": workdir,
        "title": title,
        "uploader": uploader,
        "url": webpage_url,
        "platform": platform,
        "duration": round(duration, 2),
        "has_audio": False,
        "language": None,
        "transcript": "",
        "caption": caption,
        "sheet": None,
    }

    if duration > WARN_SECONDS:
        result["warning"] = f"long video — ~{round(duration / 60)} min of audio, CPU transcribe will take many minutes"

    # 3. Audio detection + transcription
    astream = ffprobe_json(["-select_streams", "a", "-show_entries", "stream=codec_type", video])
    has_audio = bool(astream and astream.get("streams"))
    result["has_audio"] = has_audio

    if has_audio:
        wav = os.path.join(workdir, "audio.wav")
        a = run([FFMPEG, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
                 "-c:a", "pcm_s16le", wav])
        if a.returncode != 0:
            fail("audio extraction failed", detail=(a.stderr.strip().splitlines() or [""])[-1])

        w = run([WHISPERX, wav, "--model", "small", "--device", "cpu",
                 "--compute_type", "int8", "--no_align",
                 "--output_format", "txt", "--output_dir", workdir])
        if w.returncode != 0:
            fail("transcription failed", detail=(w.stderr.strip().splitlines() or [""])[-1])

        txt_path = os.path.join(workdir, "audio.txt")
        if os.path.exists(txt_path):
            with open(txt_path) as fh:
                result["transcript"] = fh.read().strip()
        # WhisperX prints "Detected language: xx" to stderr/stdout
        m = re.search(r"[Dd]etected language:?\s*([a-z]{2})", w.stderr + w.stdout)
        if m:
            result["language"] = m.group(1)

    # 4. Pass-1 contact sheet (evenly spread frames)
    sheet = os.path.join(workdir, "sheet-pass1.jpg")
    fps_val = TARGET_FRAMES / duration if duration > 0 else 1.0
    src_fps = source_fps(video)
    if src_fps:
        fps_val = min(fps_val, src_fps)
    vf = f"fps={fps_val:.6f},scale={THUMB_W}:-1,tile={GRID}"
    s = run([FFMPEG, "-y", "-i", video, "-vf", vf, "-frames:v", "1", sheet])
    if s.returncode != 0 or not os.path.exists(sheet):
        fail("frame sheet failed", detail=(s.stderr.strip().splitlines() or [""])[-1])
    result["sheet"] = sheet

    emit(result)


def cmd_scenes(args):
    workdir = args.workdir
    video = os.path.join(workdir, "video.mp4")
    if not os.path.exists(video):
        cands = [f for f in os.listdir(workdir) if f.startswith("video.") and not f.endswith(".info.json")] if os.path.isdir(workdir) else []
        if not cands:
            die("video not found in workdir", workdir=workdir)
        video = os.path.join(workdir, cands[0])

    sheet = os.path.join(workdir, "sheet-pass2.jpg")
    vf = f"select='gt(scene,{SCENE_THRESHOLD})',scale={THUMB_W}:-1,tile={GRID}"
    s = run([FFMPEG, "-y", "-i", video, "-vf", vf, "-frames:v", "1", sheet])
    if s.returncode == 0 and os.path.exists(sheet):
        emit({"sheet": sheet})
    # No frame produced means no scene changes crossed the threshold — not a failure.
    emit({"sheet": None, "note": "no scene changes above threshold"})


def cmd_cleanup(args):
    workdir = os.path.abspath(args.workdir)
    if os.path.commonpath([workdir, TMPROOT]) != TMPROOT:
        die("refusing to remove path outside TMPROOT", workdir=workdir)
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    emit({"cleaned": True})


def main():
    parser = argparse.ArgumentParser(description="video-ingest pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("prepare", help="download + transcribe + pass-1 sheet")
    p.add_argument("--url", required=True)
    p.set_defaults(func=cmd_prepare)

    sc = sub.add_parser("scenes", help="pass-2 scene-change sheet")
    sc.add_argument("--workdir", required=True)
    sc.set_defaults(func=cmd_scenes)

    cl = sub.add_parser("cleanup", help="remove the workdir")
    cl.add_argument("--workdir", required=True)
    cl.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
