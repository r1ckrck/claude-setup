#!/usr/bin/env python3
"""carousel-ingest pipeline: download an Instagram image carousel/post, collect slides + metadata.

Subcommands (each prints one line of JSON to stdout; exits non-zero with {"error": ...} on failure):
  prepare --url <URL>      download every slide + caption/uploader via gallery-dl
  cleanup --workdir <dir>  remove the workdir (must be under TMPROOT)

Cookies come from the browser named in COOKIES_FROM_BROWSER (below). Instagram gates carousel
images behind login, so the chosen browser must be logged into Instagram. To use a different
browser, change that one constant.
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

GALLERYDL = "/opt/homebrew/bin/gallery-dl"
INBOX = os.path.expanduser(os.environ.get("INGEST_INBOX", "~/inbox-remote"))
TMPROOT = os.path.expanduser(os.environ.get("INGEST_TMPROOT", "~/.cache/carousel-ingest"))

# Browser whose Instagram login cookies are used. Change this to switch browsers
# (gallery-dl supports: chrome, chromium, brave, edge, firefox, safari, opera, vivaldi).
COOKIES_FROM_BROWSER = "chrome"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")

POST_RE = re.compile(r"https?://(www\.)?instagram\.com/p/", re.I)
REEL_RE = re.compile(r"https?://(www\.)?instagram\.com/reel/", re.I)
INSTAGRAM_RE = re.compile(r"https?://(www\.)?instagram\.com/", re.I)


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


def cmd_prepare(args):
    url = args.url
    if REEL_RE.search(url):
        die("this is a reel, not a carousel", detail="use the video-ingest skill for instagram.com/reel/ links")
    if not POST_RE.search(url):
        if INSTAGRAM_RE.search(url):
            die("not a post URL", detail="carousel-ingest handles instagram.com/p/ posts; this isn't one")
        die("unsupported platform", detail="carousel-ingest handles instagram.com/p/ posts only")

    slug = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    workdir = os.path.join(TMPROOT, f"{slug}-{secrets.token_hex(2)}")
    os.makedirs(workdir, exist_ok=True)

    def fail(msg, **extra):
        """Die, but first remove the workdir we just created — no orphan temp on failure."""
        if os.path.commonpath([os.path.abspath(workdir), TMPROOT]) == TMPROOT:
            shutil.rmtree(workdir, ignore_errors=True)
        die(msg, **extra)

    # Download every slide + a metadata sidecar per image, in one pass.
    dl = run([
        GALLERYDL, "--cookies-from-browser", COOKIES_FROM_BROWSER,
        "-D", workdir, "--write-metadata", url,
    ])
    blob = (dl.stderr + dl.stdout).lower()
    # gallery-dl exits 0 even when it bounces to the login page, so detect that from output.
    if "login" in blob or "redirect" in blob:
        fail("instagram login required",
             detail=f"log into Instagram in {COOKIES_FROM_BROWSER} (or change COOKIES_FROM_BROWSER), then retry")
    if dl.returncode != 0:
        last = (dl.stderr.strip().splitlines() or ["unknown error"])[-1]
        fail("download failed", detail=last)

    images = sorted(
        os.path.join(workdir, f) for f in os.listdir(workdir)
        if f.lower().endswith(IMAGE_EXTS)
    )
    if not images:
        fail("no images downloaded",
             detail="the post may be video-only, private, or login is required")

    # Read one metadata sidecar for caption/uploader (gallery-dl writes <image>.json per slide).
    meta = {}
    for f in os.listdir(workdir):
        if f.endswith(".json"):
            try:
                with open(os.path.join(workdir, f)) as fh:
                    meta = json.load(fh)
            except (OSError, json.JSONDecodeError):
                meta = {}
            break

    uploader = meta.get("username") or meta.get("owner") or "(unknown)"
    fullname = meta.get("fullname") or ""
    caption = meta.get("description") or ""
    webpage_url = meta.get("post_url") or url
    date = meta.get("date") or ""

    emit({
        "slug": slug,
        "out_name": f"{slug}-carousel-ingest",
        "workdir": workdir,
        "platform": "Instagram",
        "url": webpage_url,
        "uploader": uploader,
        "fullname": fullname,
        "caption": caption,
        "date": str(date),
        "image_count": len(images),
        "images": images,
        "cookie_browser": COOKIES_FROM_BROWSER,
    })


def cmd_cleanup(args):
    workdir = os.path.abspath(args.workdir)
    if os.path.commonpath([workdir, TMPROOT]) != TMPROOT:
        die("refusing to remove path outside TMPROOT", workdir=workdir)
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    emit({"cleaned": True})


def main():
    parser = argparse.ArgumentParser(description="carousel-ingest pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("prepare", help="download slides + metadata")
    p.add_argument("--url", required=True)
    p.set_defaults(func=cmd_prepare)

    cl = sub.add_parser("cleanup", help="remove the workdir")
    cl.add_argument("--workdir", required=True)
    cl.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
