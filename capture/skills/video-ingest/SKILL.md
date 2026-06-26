---
name: video-ingest
description: When an Instagram or YouTube video URL is shared or given, fetch it and turn it into routable text — download the video and caption, transcribe the audio, read on-screen text and links from sampled frames, and write one markdown file to inbox-remote/. Use whenever a message or captured item contains an instagram.com or youtube.com/youtu.be video link.
allowed-tools: Bash(/opt/homebrew/opt/python@3.13/libexec/bin/python3:*), Read, Write
---

# Video Ingest

Turns a shared Instagram or YouTube video URL into one readable markdown file in `inbox-remote/` — downloads it, transcribes the speech, and reads the on-screen frames (where URLs, handles, and overlays live that the audio never says), then writes a clean summary for routing.

## When to use

| Trigger | Action |
|---|---|
| A message contains an `instagram.com` or `youtube.com` / `youtu.be` video link | Run the workflow below |
| An ingested capture is essentially just such a URL | Same — expand it before it gets filed as a bare link |

Out of scope: any other platform; private / login-walled / removed videos (the run stops and tells the user).

## How it works

The deterministic media work lives in `scripts/video_ingest.py` (three subcommands, each prints one line of JSON). The judgment — reading the contact sheet, deciding whether a second frame pass is needed, writing the summary — is yours.

Invoke the script with the pinned interpreter:

```
PY=/opt/homebrew/opt/python@3.13/libexec/bin/python3
S=.claude/skills/video-ingest/scripts/video_ingest.py
```

## Workflow

1. **Confirm the URL** is Instagram or YouTube. If not, it's out of scope — say so, do nothing.

2. **Run `prepare`:**
   ```
   "$PY" "$S" prepare --url "<URL>"
   ```
   - On `{"error": ...}` → **STOP.** Tell the user the cause in plain words (e.g. "yt-dlp couldn't fetch it — the video is private or removed"). Write nothing. If a `workdir` was created, run `cleanup` on it.
   - If the result has a `warning` (long video) → tell the user the estimate and **confirm before continuing** the transcribe.
   - Otherwise you get JSON with `out_name`, `workdir`, `sheet`, `transcript`, `caption`, and the metadata used in the output below.

3. **Read the pass-1 contact sheet** (`sheet`) with vision. Extract *every* legible on-screen string — URLs, @handles, product names, overlay captions, prices, lower-thirds, UI labels. This is where the real content often is; the audio rarely says the URL.

4. **Decide on pass 2.** Run it ONLY when both are true: the video is text- or tutorial-heavy, AND pass 1 looks like it skipped cuts (e.g. the transcript says "link below" / "the site" but no URL surfaced, or tiles are mid-transition blur). A plain talking-head with all overlays already captured does **not** need pass 2.

5. **If needed, run `scenes`:**
   ```
   "$PY" "$S" scenes --workdir "<workdir>"
   ```
   Read `sheet-pass2.jpg` and merge any new strings. If it returns `{"sheet": null}`, there were no scene changes — proceed with what you have.

6. **Write the markdown** to `inbox-remote/<out_name>.md` (the `out_name` from `prepare`, e.g. `2026-06-03-142530-video-ingest`) using the structure below.

7. **Run `cleanup`:**
   ```
   "$PY" "$S" cleanup --workdir "<workdir>"
   ```

8. **Report** one line: `ingested → inbox-remote/<out_name>.md`.

The pass-1 → judge → pass-2 loop runs at most once.

## Output structure

Write to `inbox-remote/<out_name>.md` (the `out_name` from `prepare`, format `YYYY-MM-DD-HHMMSS-video-ingest`):

```markdown
# <title>

- Source: <url>
- Uploader: <uploader>
- Platform: <Instagram | YouTube>
- Duration: <m:ss>
- Captured: <YYYY-MM-DD>

## Caption
<caption verbatim; "(none)" if empty>

## Spoken transcript
<transcript; "(no audio track)" if has_audio is false; "(no speech detected)" if audio but empty>

## On-screen text & links
- <every URL / handle / overlay string read from the sheet(s), deduped>

## Synthesis
<2–4 sentences: what the video is, the actionable takeaway, why it was likely shared. This is the routable summary.>
```

Keep it quiet and plain — no decoration.
