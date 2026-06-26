"""Orchestration helpers for fal-video: slug, version, sidecar, preamble strip, download."""

import json
import re
import shutil
import unicodedata
import urllib.request
from pathlib import Path


_FILLER_WORDS = {
    "a", "an", "the",
    "of", "for", "with", "to", "in", "on", "at", "by", "from",
    "please", "can", "you", "could", "would", "give", "make", "create",
    "generate", "design", "show", "build",
    "me", "us", "my", "our", "your", "i",
    "and", "or", "but",
}

_VERSION_TOKEN_RE = re.compile(r"\b(?:v\.?\s*\d+|version\s+\d+)\b", re.IGNORECASE)
_PUNCTUATION_RE = re.compile(r"[^\w\s\-]")
_PREAMBLE_LINE_RE = re.compile(
    r"^(now\s+i|let\s+me|let's|here'?s?|i'll|i\s+will|constructing|"
    r"building|composing|drafting|the\s+prompt|prompt:|output:|final|"
    r"based\s+on|considering|analyzing|step\s+\d|first|next|then,?\s|"
    r"reading|loading|locked|inputs|using\s+the)",
    re.IGNORECASE,
)


def slug_from_request(request, fallback_subject=None):
    """Derive a filesystem slug per outputs.md rules. Falls back to 'untitled'."""
    text = _VERSION_TOKEN_RE.sub("", request)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = _PUNCTUATION_RE.sub(" ", text).lower()
    tokens = [t for t in text.split() if t and t not in _FILLER_WORDS]
    tokens = tokens[:6]
    slug = "-".join(tokens).strip("-")
    if len(slug) < 3:
        if fallback_subject:
            return slug_from_request(fallback_subject)
        return "untitled"
    return slug


def next_version(folder, slug):
    """Scan folder for <slug>-vNN.*; return next 'vNN' string. Expands past v99."""
    folder = Path(folder)
    if not folder.exists():
        return "v01"
    pattern = re.compile(rf"^{re.escape(slug)}-v(\d+)\.")
    versions = [int(m.group(1)) for entry in folder.iterdir() if (m := pattern.match(entry.name))]
    n = max(versions) + 1 if versions else 1
    return f"v{n:02d}"


def write_sidecar(path, data):
    """Write a sidecar JSON file pretty-printed. Returns bytes written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    size = path.stat().st_size
    if size == 0:
        raise IOError(f"sidecar wrote zero bytes: {path}")
    return size


def strip_preamble(text):
    """Strip leading meta-narration from brief-constructor output."""
    lines = text.strip().split("\n")
    while lines:
        first = lines[0].strip()
        if not first:
            lines.pop(0)
            continue
        if first.startswith("#") or first.startswith("```") or first.startswith(">"):
            lines.pop(0)
            continue
        if _PREAMBLE_LINE_RE.match(first) and len(first) < 200:
            lines.pop(0)
            continue
        break
    return "\n".join(lines).strip()


def download_to_local(url, dest_path, timeout=120):
    """Download a URL to a local path. Returns bytes written."""
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "vizkit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response, dest_path.open("wb") as out:
        shutil.copyfileobj(response, out)
    size = dest_path.stat().st_size
    if size == 0:
        raise IOError(f"download wrote zero bytes: {dest_path}")
    return size
