"""webfetch connector — pulls metadata from a live URL (e.g. a personal site).
stdlib only: urllib for the request, html.parser for extraction."""

import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.desc = None
        self.headings = []
        self.links = 0
        self._in_title = False
        self._in_h = None
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2"):
            self._in_h = tag
            self._buf = ""
        elif tag == "a" and a.get("href"):
            self.links += 1
        elif tag == "meta" and (a.get("name", "").lower() == "description" or a.get("property", "") == "og:description"):
            if not self.desc and a.get("content"):
                self.desc = a["content"]

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == self._in_h:
            if self._buf.strip():
                self.headings.append(self._buf.strip())
            self._in_h = None

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        elif self._in_h:
            self._buf += data


def discover(config):
    items = []
    for url in config.get("urls", []):
        host = url.split("//")[-1].split("/")[0]
        items.append({"uri": url, "type": "webfetch", "role": "live", "name": host, "meta": {}})
    return items


def fetch_meta(uri, config):
    req = urllib.request.Request(uri, headers={"User-Agent": "project-vault"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read(500000).decode("utf-8", "replace")
        header_lm = r.headers.get("Last-Modified")
    p = _Extract()
    p.feed(raw)
    title = (p.title or "").strip() or uri
    return {
        "name": title,
        "last_modified": header_lm or _now(),
        "visibility": "public",
        "description": (p.desc or "").strip()[:300],
        "headings": p.headings[:12],
        "link_count": p.links,
    }
