---
name: carousel-ingest
description: When an Instagram image post or carousel URL is shared or given (an instagram.com/p/ link, often a multi-slide carousel), fetch every slide and turn it into routable text — download the images and caption, read each slide with vision, and write one markdown file to inbox-remote/. Use whenever a message or captured item is essentially an instagram.com/p/ post link. For instagram.com/reel/ video links, use video-ingest instead.
allowed-tools: Bash(/opt/homebrew/opt/python@3.13/libexec/bin/python3:*), Read, Write
---

# Carousel Ingest

Turns a shared Instagram **image post / carousel** (`instagram.com/p/…`) into one readable markdown file in `inbox-remote/` — downloads every slide and the caption, reads each slide with vision (where the URLs, handles, and copy live), then writes a clean summary for routing.

This is the image-post companion to `video-ingest`. Reels and YouTube (video) go to `video-ingest`; this handles multi-image posts.

## When to use

| Trigger | Action |
|---|---|
| A message contains an `instagram.com/p/` link | Run the workflow below |
| An ingested capture is essentially just such a URL | Same — expand it before it gets filed as a bare link |

Out of scope: `instagram.com/reel/` and YouTube (→ `video-ingest`); any other platform; private / unavailable posts (the run stops and tells the user).

## Login is required

Instagram gates carousel images behind login, so this skill reads your **browser's Instagram cookies**. It uses **Chrome** by default. The chosen browser must be logged into Instagram. To switch browsers, change the `COOKIES_FROM_BROWSER` constant in `scripts/carousel_ingest.py`.

## How it works

The deterministic media work lives in `scripts/carousel_ingest.py` (two subcommands, each prints one line of JSON). The judgment — reading the slides, writing the summary — is yours.

Invoke the script with the pinned interpreter:

```
PY=/opt/homebrew/opt/python@3.13/libexec/bin/python3
S=.claude/skills/carousel-ingest/scripts/carousel_ingest.py
```

## Workflow

1. **Confirm the URL** is an `instagram.com/p/` post. If it's a `/reel/` or another platform, it's out of scope — hand it to `video-ingest` or say so.

2. **Announce the cookie source** to the user before downloading, so a different setup can be adjusted:
   > Pulling Instagram cookies from **Chrome**. To use another browser, change `COOKIES_FROM_BROWSER` in `carousel_ingest.py`.

3. **Run `prepare`:**
   ```
   "$PY" "$S" prepare --url "<URL>"
   ```
   - On `{"error": "instagram login required"}` → **STOP.** Tell the user: open Chrome, confirm you're logged into Instagram, then retry. (Chrome cookies can go stale after it's been closed a while; launching it refreshes them.) Write nothing.
   - On any other `{"error": ...}` → **STOP.** Tell the user the cause in plain words. If a `workdir` was created it's already cleaned; nothing to do.
   - Otherwise you get JSON with `out_name`, `workdir`, `uploader`, `caption`, `image_count`, `images` (ordered slide paths), and the metadata used below.

4. **Read every slide** in `images` order with vision. Extract *all* legible content per slide — headings, body copy, URLs, @handles, product/tool names, prices, anything on-screen. The slides carry the real content; the caption is usually thin.

5. **Write the markdown** to `inbox-remote/<out_name>.md` (the `out_name` from `prepare`, format `YYYY-MM-DD-HHMMSS-carousel-ingest`) using the structure below.

6. **Run `cleanup`:**
   ```
   "$PY" "$S" cleanup --workdir "<workdir>"
   ```

7. **Report** one line: `ingested → inbox-remote/<out_name>.md`.

## Output structure

Write to `inbox-remote/<out_name>.md`:

```markdown
# <title — the cover-slide headline, or "(untitled)">

- Source: <url>
- Uploader: <uploader>
- Platform: Instagram
- Slides: <image_count>
- Captured: <YYYY-MM-DD>

## Caption
<caption verbatim; "(none)" if empty>

## Slides
1. <key content read from slide 1>
2. <slide 2>
…

## Links & handles
- <every URL / @handle read across the slides, deduped>

## Synthesis
<2–4 sentences: what the carousel is, the actionable takeaway, why it was likely shared. This is the routable summary.>
```

Keep it quiet and plain — no decoration.
